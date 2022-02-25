import traceback
from datetime import datetime, timedelta
from multiprocessing import Event, Manager, Process
from time import sleep

from control import Control
from sensors import Sensors
from interval import IntervalThread


class SensorProcess(Process):
    def __init__(self, lproxy):
        Process.__init__(self)
        self.exit = Event()
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

            while True:
                sleep(1)

    def shutdown(self):
        print("Killing SensorProcess...")
        self.exit.set()
        print("SensorProcess killed.")


class ControlProcess(Process):
    def __init__(self, lproxy):
        Process.__init__(self)
        self.exit = Event()
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

            while not ctrl.is_queued_msgs() or not ctrl.peek_next_msg().ARMED:
                print(ctrl.commands)  # TODO: Remove debug stmt
                if ctrl.is_queued_msgs():
                    ctrl.get_next_msg()
                else:
                    sleep(1)
            ctrl.set_end_time()

            print("ARMED")
            while True:
                # Control loop to determine radio disconnection
                ctrl.safetyTimer()
                result = ctrl.is_queued_msgs()
                # Wait 5 min. to reestablish signal
                endT = datetime.now() + timedelta(hours=3)
                while result == 0 and datetime.now() < endT:
                    ctrl.safetyTimer()
                    result = ctrl.is_queued_msgs()
                    sleep(0.5)  # Don't overload CPU

                # These don't need to be parallel to the radio connection, since we won't
                # be getting commands if the radjjio is down
                if result == 0 and (not ctrl.groundAbort()):
                    ctrl.qdm_check(1)
                else:
                    # Receive commands and iterate through them
                    commands = ctrl.get_next_msg()
                    if ctrl.getLaunchFlag():
                        print("Launch Detected")
                        ctrl.ignition(mode)
                    if ctrl.getQDMFlag():
                        print("QDM Detected")
                        ctrl.qdm_check(1)
                    if ctrl.getAbortFlag():
                        print("Abort Detected")
                        ctrl.groundAbort(1)
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
    except Exception:
        print("exception caught")
        traceback.print_exc()
    finally:  # Catch interrupts (terminates with traceback)
        print("Ending processes...")
        data.shutdown()
        comm.shutdown()
        sleep(1)  # Wait until processes close
        print("Processes terminated.\n")


if __name__ == "__main__":
    main()