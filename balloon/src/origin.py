from multiprocessing import Process, Manager
from datetime import datetime, timedelta
from data_aggr import Sensors
from comm_parse import Control
from time import sleep


def dataProc(d):
    """
    Main process for data_aggr.py
    Initializes sensor package module and passes data to the RadioModule
    (and comm_parse.py using a Manager())
    """

    print("Running data_aggr.py ...\n")
    sens = Sensors("Balloon Computer")

    while True:
        sens.read_all()  # send every data point to radio/command? Bad idea
        sens.send()
        sens.pass_to(d)


def commProc(d):
    """
    Controls all command processes for the balloon flight computer. Gets data
    from dataProc using a DictProxy managed by Manager() in main.
    """

    print("Running comm_parse.py ...\n")

    ctrl = Control(5, 6, rocketlogpin, 13, 0.05) #rocketlogpin currently undefined
    #pin number 13 = stabilization pin

    mode = 1 # mode 1 = testmode / mode 2 = pre-launch mode

    result = ctrl.connection_check()
    endT = datetime.now() + timedelta(seconds = 10)
    while ((result == None) & (datetime.now() < endT)):
        result = ctrl.connection_check()
    if result == 0:
        ctrl.QDMCheck(0)
    else:
        ctrl.receivedata()
        while not ctrl.commands.empty():
            GSDATA = ctrl.commands.get()
    
            CType = GSDATA['command']
            if (CType == 'QDM'):
                ctrl.QDMCheck(0)
            if (CType == 'Stabilize'):
                ctrl.Stabilization(d)
            if (CType == 'Ignition'):
                ctrl.Ignition(mode,d)

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
