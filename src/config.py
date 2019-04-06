from multiprocessing import Process, Manager
from datetime import datetime, timedelta
from data_aggr import SerialPort
from comm_parse import Control

def dataProc(d):
    """
    Main process for data_aggr.py
    Initializes serial port connected to Arduino-controlled sensor
    module, and passes data to the RadioModule (and comm_parse.py
    using a Manager())
    """
    print("Running data_aggr.py ...\n")
    # Create new serial port for sensor arduino with name and USB port path
    try:
        port = "/dev/ttyUSB0"
        ino = SerialPort("SensorModule", port)

        ino.speedTest(10)

        while True: # Iterates infinitely, sending JSON objects over radio
            ino.JSONpass(d)

    except OSError:     # Raised when Arduino isn't connected
        print("No such file or directory {}.\n".format(port))
    except KeyboardInterrupt:
        print("Program closed by user.\n")

def commProc(d):
    """
    Controls all command processes for the balloon flight computer.
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
    d = Manager().dict()
    data = Process(target=dataProc, args=(d,))
    comm = Process(target=commProc, args=(d,))
    data.start()
    comm.start()
