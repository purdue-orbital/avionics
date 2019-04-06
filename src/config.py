from multiprocessing import Process, Manager
from data_aggr import SerialPort
# from comm_parse import Control

def dataProc(d):
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

if __name__ == "__main__":
    d = Manager().dict()
    data = Process(target=dataProc, args=(d,))
    data.start()
