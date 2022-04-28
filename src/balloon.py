import setenv  # Sets PYTHONPATH / other envvars, must be imported first

from datetime import datetime, timedelta
from multiprocessing import Event, Manager, Process
from time import sleep
import traceback

from interval import IntervalThread

from control import Control
from sensors import Sensors


class SensorProcess(Process):
    def __init__(self, lproxy):
        Process.__init__(self)
        self.exit = Event()  # FIXME: Event never used
        self.proxy = lproxy

    def run(self):
        """
        Main process for sensors.py
        Initializes sensor package module and passes data to the RadioModule
        (and comm_parse.py using a Manager())
        """
        print("Running sensors.py ...")

        with Sensors("balloon") as sensors:
            # Lambda used to pass generic multi-arg functions to sensors.add
            # These will later be executed in unique threads
            sensors.add(
                lambda: sensors.temperature(write=True),
                1,
                identity="temp",
                token="temp (C)",
                access=lambda: sensors.temperature(),
            )

            sensors.add(
                lambda: sensors.gps(write=True),
                0.5,
                identity="GPS",
                token="lat, long, alt (m)",
                access=lambda: sensors.gps(),
            )

            sensors.add(
                lambda: sensors.accel(write=True),
                2,
                identity="acc",
                token="ax (g),ay (g),az (g)",
                access=lambda: sensors.accel(),
            )

            sensors.add(
                lambda: sensors.gyro(write=True),
                2,
                identity="gyro",
                token="gx (dps),gy (dps),gz (dps)",
                access=lambda: sensors.gyro(),
            )
            sensors.add(lambda: sensors.pass_to(self.proxy, "GPS", "gyro"), 2)

            # sensors.add(lambda: sensors.send(), 1)

            ### DON'T CHANGE ###
            sensors.add(lambda: sensors.time(), sensors.greatest, token="time (s)")
            sensors.write_header()
            sensors.add(lambda: sensors.write(), sensors.greatest)
            sensors.stitch()
            ### DON'T CHANGE ###

            while True:  # FIXME: Use event here??
                sleep(1)

    def shutdown(self):
        print("Killing SensorProcess...")
        self.exit.set()
        print("SensorProcess killed.")


class ControlProcess(Process):
    def __init__(self, lproxy):
        Process.__init__(self)
        self.exit = Event()  # FIXME: Event never used
        self.proxy = lproxy

    def run(self):
        """
        Controls all command processes for the balloon flight computer.
        """
        print("Running control.py ...\n")

        with Control("balloon") as ctrl:
            mode = 2  # mode 1 = testmode / mode 2 = pre-launch mode
            # Data collection needs to be running parallel to rest of program
            collect = IntervalThread(lambda: ctrl.read_data(self.proxy), 1)
            collect.start()

            # Wait untill a Msg with an ARMED flag is received
            while not ctrl.is_queued_msgs() or not ctrl.peek_next_msg().ARMED:
                if ctrl.is_queued_msgs():
                    ctrl.pop_next_msg()
                else:
                    sleep(1)
            ctrl.set_end_time()  # Set an amount of time before panicing
            max_flight_time = datetime.now() + timedelta(
                hours=48
            )  # Max flight time before panicing

            print("ARMED")

            while True:
                # Control loop to determine radio disconnection
                ctrl.safetyTimer()

                now = datetime.now()
                if now > ctrl.endT or now > max_flight_time:
                    # PANIC!!
                    print("Flight Time Exceded, Safety QDM Engaged")

                    # Not sure what ground_abort is or why it is checked
                    # Simply adding additional check for backward compatability
                    if not ctrl.ground_abort:
                        ctrl.set_ground_abort(True)
                        ctrl.set_qdm(True)
                elif ctrl.is_queued_msgs():
                    # Receive commands and iterate through them
                    ctrl.pop_next_msg()
                    # FIXME: Queue messages are never used, could just unbind queue here
                    # or use orbitalcoms.LaunchStation.getArmedFlag() to detect armed

                    ctrl.set_end_time()  # Reset panic timer
                    if ctrl.getLaunchFlag():
                        print("Launch Detected")
                        ctrl.ignition(mode)
                    if ctrl.getQDMFlag():
                        print("QDM Detected")
                        ctrl.set_qdm(True)
                    if ctrl.getAbortFlag():
                        print("Abort Detected")
                        ctrl.set_ground_abort(True)
                        ctrl.abort()
                    if ctrl.getStabFlag():
                        print("Stabilize Detected")
                        ctrl.stabilization()
                sleep(1)

    #            ctrl.qdm_check(0)
    #            sleep(3)
    #            ctrl.ignition(2)

    def shutdown(self):
        print("Killing ControlProcess...")
        self.exit.set()
        print("ControlProcess killed.")


def main() -> None:
    try:
        # Create Manager() for dict (which is stored in a list)
        manager = Manager()
        # Dict stored in lproxy[0] for syncing reasons
        # FIXME: Why are we using a managed list when mp.Manger.dict exists???
        lproxy = manager.list()
        lproxy.append({})

        # Assign each function to a Process
        data = SensorProcess(lproxy)
        comm = ControlProcess(lproxy)
        # Start processes
        comm.start()
        data.start()
        # Wait in main so that this can be escaped properly with ctrl+c
        data.join()
        comm.join()
    except:
        print("exception caught")
        data.shutdown()
        comm.shutdown()
        traceback.print_exc()
    finally:  # Catch interrupts (terminates with traceback)
        print("Ending processes...")
        sleep(1)  # Wait until processes close
        print("Processes terminated.\n")


if __name__ == "__main__":
    main()
