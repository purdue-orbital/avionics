from multiprocessing import Process, Manager
from datetime import datetime, timedelta
from sensors import Sensors
from control import Control
from time import sleep

def dataProc(lproxy):
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
        sensors.add(lambda: sensors.pass_to(lproxy, "alt", "gyro"), 1)

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
   

def commProc(lproxy):
    """
    Controls all command processes for the balloon flight computer. Gets data
    from dataProc using a DictProxy managed by Manager() in main.
    """

    print("Running control.py ...\n")

    ctrl = Control(5, 6, 22, 13) #rocketlogpin currently undefined
    # pin 13 = stabilization pin
    # pin 22 = rocket out pin

    mode = 1 # mode 1 = testmode / mode 2 = pre-launch mode

    result = ctrl.connection_check()
    endT = datetime.now() + timedelta(seconds = 10)
    while ((result == None) & (datetime.now() < endT)):
        result = ctrl.connection_check()
    if result == 0:
        ctrl.qdm_check(0)
    else:
        ctrl.receive_data()
        while not ctrl.commands.empty():
            GSDATA = ctrl.commands.get()
    
            CType = GSDATA['command']
            if (CType == 'QDM'):
                ctrl.qdm_check(0)
            if (CType == 'Stabilize'):
                ctrl.stabilization(lproxy)
            if (CType == 'Ignition'):
                ctrl.ignition(mode)

        ## NEED CHANGES ###
        #rocket = d
   # balloon = Manager
            
    #ctrl.readdata(d)
        
       # condition = ctrl.dataerrorcheck()
       # mode = 1
       # if (IGNITION):
       #     ctrl.Ignition(mode)


if __name__ == "__main__":
    try:
        # Create Manager() for dict (which is stored in a list)
        manager = Manager()
        # Dict stored in lproxy[0] for syncing reasons
        lproxy = manager.list()
        lproxy.append({})

        # Assign each function to a Process
        data = Process(target=dataProc, args=(lproxy,))
        # comm = Process(target=commProc, args=(lproxy,))

        # Start processes
        data.start()
        # comm.start()
        # Wait in main so that this can be escaped properly with ctrl+c
        while True:
            sleep(10)

    except KeyboardInterrupt:  # Catch interrupts (terminates correctly)
        print("Ending processes...")
        data.terminate()
        # comm.terminate()
        print("Processes terminated.\n")
