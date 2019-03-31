import serial
import json
import time
import os.path

class SerialPort():
    """
    Object to control serial port functionality.
    """

    def __init__(self, name, port):
        """
        Initializes the Port object

        Args:
            Name: String ID for serial port 
            Port: USB connection for Arduino in '/dev/tty*'
        """
        print("\nInitializing {} on port {}...".format(name, port))
        self.name = name
        self.port = port    # serial connection port
        self.blankDict = {"altitude": None,
        "GPS": {
            "longitude": None,
            "latitude": None
            },
        "Gyroscope": {
            "x": None,
            "y": None,
            "z": None
            },
        "Magnetometer": None,
        "Temperature": None,
        "Accelerometer": {
            "x": None,
            "y": None,
            "z": None
            }
        }
        self.ser = serial.Serial(self.port, 115200)   # -, baud rate (from Arduino)
        self.path = os.path.dirname(os.path.realpath(__file__)) # file path

        print("Initialization complete.")
    
    def writeDict(self):
        """
        Reads from Serial connection and writes to .json

        Args:
            file: .json file to write on
        """
        ln = self.ser.readline()
        if ln.split(':')[0] == "ERROR":
            pass
        else:
            '''
            lst = ln.split(',')
            # TODO: Work out printing
            '''
            print(ln)

    def JSONpass(self, fname):
        """
        Creates a .json file every second and populates it with data from
        serial connection

        Args:
            fname: current date name for json file
        """
        with open(os.path.join(self.path, "send", fname), "w") as file:
            t_end = time.time() + 60
            self.currentDict = self.blankDict

            while time.time() < t_end:
                self.writeDict()
            
            json.dump(self.currentDict, file)

if __name__ == "__main__":
    # Create new serial port for sensor arduino with name and USB port path
    # TODO: Find actual path on Pi
    ino = SerialPort("SensorModule", "/dev/tty")

    while True: # Iterates infinitely, writing new .json files to ~/Avionics/send
        ino.JSONpass(str(int(time.time()*1000)) + ".json")   # ms since 1/1/1970
            