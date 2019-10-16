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
    sens = Sensors("MPU9250")

    while True:
        sens.readAll() # send every data point to radio/command? Bad idea
        sens.send()
        sens.passTo(d)

def commProc(d):
    """
    Controls all command processes for the balloon flight computer. Gets data
    from dataProc using a DictProxy managed by Manager() in main.
    """
    
    print("Running comm_parse.py ...\n")
    ctrl = Control(5,6,0.05)

    result = ctrl.ConnectionCheck()
    endT = datetime.now() + timedelta(seconds = 10)
    while ((result == 0) & (datetime.now() < endT)):
        result = ctrl.ConnectionCheck()
    if (result == 0):
        ctrl.QDMCheck(0)
    else:
        while not ctrl.commands.empty():
            GSDATA = ctrl.receivedata()
    
            QDM = GSDATA['QDM']
            IGNITION = GSDATA['Ignition']
            #    CDM = GSDATA['CDM']
            #    STAB = GSDATA['Stabilization']
            #    CRASH = GSDATA['Crash']
            #    DROGUE = GSDATA['Drogue']
            #    MAIN_CHUTE = GSDATA['Main_Chute']

            ctrl.QDMCheck(QDM)

        ## NEED CHANGES ###
        rocket = d
        balloon = d
            
        ctrl.readdata(rocket,balloon)
        
        condition = ctrl.dataerrorcheck()
        mode = 1
        if (condition & IGNITION):
            ctrl.Ignition(mode)

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
        
    except KeyboardInterrupt:   # Catch interrupts (terminates correctly)
        print("Ending processes...")
        data.terminate()
        # comm.terminate()
        print("Processes terminated.\n") 
