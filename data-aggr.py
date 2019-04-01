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
        self.blankDict = {"Pressure": [],   # Initialize dictionary structure
        "GPS": {
            "longitude": [],
            "latitude": []
            },
        "Gyroscope": {
            "x": [],
            "y": [],
            "z": []
            },
        "Magnetometer": {
            "x": [],
            "y": [],
            "z": []
            },
        "Temperature": [],
        "Accelerometer": {
            "x": [],
            "y": [],
            "z": []
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
        ln = self.ser.readline().rstrip()
        if ln.split(':')[0] == "ERROR":
            pass    # Don't write if given an error message
        else:
            # Break string into array
            lst = ln.split(', ')
            # Assigning each value in given list to dict entry
            self.currentDict["Pressure"].append(lst[0])
            self.currentDict["GPS"]["longitude"].append(lst[1])
            self.currentDict["GPS"]["latitude"].append(lst[2])
            self.currentDict["Gyroscope"]["x"].append(lst[3])
            self.currentDict["Gyroscope"]["y"].append(lst[4])
            self.currentDict["Gyroscope"]["z"].append(lst[5])
            self.currentDict["Magnetometer"]["x"].append(lst[6])
            self.currentDict["Magnetometer"]["y"].append(lst[7])
            self.currentDict["Magnetometer"]["z"].append(lst[8])
            self.currentDict["Temperature"].append(lst[9])
            self.currentDict["Accelerometer"]["x"].append(lst[10])
            self.currentDict["Accelerometer"]["y"].append(lst[11])
            self.currentDict["Accelerometer"]["z"].append(lst[12])

    def JSONpass(self, fname):
        """
        Creates a .json file and populates it with one second's worth of data
        from serial connection

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
    ino = SerialPort("SensorModule", "/dev/ttyUSB0")

    while True: # Iterates infinitely, writing new .json files to ~/Avionics/send
        ino.JSONpass(str(int(time.time()*1000)) + ".json")   # ms since 1/1/1970
            