import serial
import json
import time

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
        self.json = {"Pressure": 0,   # Initialize dictionary structure
        "GPS": {
            "longitude": 0,
            "latitude": 0
            },
        "Gyroscope": {
            "x": 0,
            "y": 0,
            "z": 0
            },
        "Magnetometer": {
            "x": 0,
            "y": 0,
            "z": 0
            },
        "Temperature": 0,
        "Accelerometer": {
            "x": 0,
            "y": 0,
            "z": 0
            }
        }
        self.ser = serial.Serial(self.port, 115200)   # -, baud rate (from Arduino)
        print("Initialization complete.")

    def writeDict(self):
        """
        Reads from Serial connection and writes to dict
        """
        ln = self.ser.readline().decode('utf-8').rstrip()
        if ln.split(':')[0] == "ERROR":
            pass    # Don't write if given an error message
        else:
            # Break string into array
            lst = ln.split(', ')
            # Assigning each value in given list to dict entry
            self.json["Pressure"] = lst[0]
            self.json["GPS"]["longitude"] = lst[1]
            self.json["GPS"]["latitude"] = lst[2]
            self.json["Gyroscope"]["x"] = lst[3]
            self.json["Gyroscope"]["y"] = lst[4]
            self.json["Gyroscope"]["z"] = lst[5]
            self.json["Magnetometer"]["x"] = lst[6]
            self.json["Magnetometer"]["y"] = lst[7]
            self.json["Magnetometer"]["z"] = lst[8]
            self.json["Temperature"] = lst[9]
            self.json["Accelerometer"]["x"] = lst[10]
            self.json["Accelerometer"]["y"] = lst[11]
            self.json["Accelerometer"]["z"] = lst[12]

    def JSONpass(self):
        """
        Overwrites dict with sensor data and sends over radio
        """
        self.writeDict()
        # print(self.json)

if __name__ == "__main__":
    # Create new serial port for sensor arduino with name and USB port path
    try:
        port = "/dev/ttyUSB0"
        ino = SerialPort("SensorModule", port)

        while True: # Iterates infinitely, sending JSON objects over radio
            ino.JSONpass()

    except OSError:
        print("No such file or directory {}.\n".format(port))
    except KeyboardInterrupt:
        print("Program closed by user.\n")
