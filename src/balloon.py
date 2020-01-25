from multiprocessing import Process, Manager, Event
from datetime import datetime, timedelta
from sensors import Sensors
from control import Control
from time import sleep

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
        print("Running sensors.py ...\n")

        with Sensors("balloon") as sensors:
            # Lambda used to pass generic multi-arg functions to sensors.add
            # These will later be executed in unique threads
            sensors.add(lambda: sensors.temperature(write=True), 1, identity="temp",
                token="temp (C)", access=lambda: sensors.temperature()
            )

            sensors.add(lambda: sensors.gps(write=True), 0.5, identity="GPS",
                token="lat, long, alt (m)", access=lambda: sensors.gps()
            )

            sensors.add(lambda: sensors.accel(write=True), 1, identity="acc",
                token="ax (g),ay (g),az (g)", access=lambda: sensors.accel()
            )

            sensors.add(lambda: sensors.gyro(write=True), 2, identity="gyro",
                token="gx (dps),gy (dps),gz (dps)", access=lambda: sensors.gyro()
            )
            sensors.add(lambda: sensors.pass_to(self.proxy, "GPS", "gyro"), 1)

            # sensors.add(lambda: sensors.send(), 1)

            
            ### DON'T CHANGE ###
            sensors.add(lambda: sensors.time(), sensors.greatest, token="time (s)")
            sensors.write_header()
            sensors.add(lambda: sensors.write(), sensors.greatest)
            sensors.stitch()
            ### DON'T CHANGE ###
            
            while True:
                sensors.print()
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
            mode = 2 # mode 1 = testmode / mode 2 = pre-launch mode

            # Data collection needs to be running parallel to rest of program
            collect = ctrl.Collection(lambda: ctrl.read_data(self.proxy), 1)
            collect.start()
            """
            while True:
                # Control loop to determine radio disconnection
                result = ctrl.connection_check()
                endT = datetime.now() + timedelta(seconds=300)  # Wait 5 min. to reestablish signal
                while ((result == None) & (datetime.now() < endT)):
                    result = ctrl.connection_check()
                    sleep(0.5)  # Don't overload CPU

                # These don't need to be parallel to the radio connection, since we won't
                # be getting commands if the radio is down
                if result == 0:
                    ctrl.qdm_check(0)
                else:
                    # Receive commands and iterate through them
                    ctrl.receive_data()
                    while not ctrl.commands.empty():
                        GSDATA = ctrl.commands.get()

                        CType = GSDATA['command']
                        if (CType == 'QDM'):
                            ctrl.qdm_check(0)
                        # Are ignition and stabilize same signal?
                        if (CType == 'Stabilize'):
                            ctrl.stabilization()
                        if (CType == 'Ignition'):
                            ctrl.ignition(mode)
            """
            sleep(5)
            # ctrl.stabilization()
            while True:
                sleep(2)

    def shutdown(self):
        print("Killing ControlProcess...")
        self.exit.set()
        print("ControlProcess killed.")


if __name__ == "__main__":
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
        data.start()
        comm.start()
        # Wait in main so that this can be escaped properly with ctrl+c
        data.join()
        comm.join()

    finally:  # Catch interrupts (terminates with traceback)
        print("Ending processes...")
        data.shutdown()
        comm.shutdown()
        sleep(2)  # Wait until processes close
        print("Processes terminated.\n")
