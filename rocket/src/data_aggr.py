import serial
import json
import time
from RadioModule import Module

class SerialPort():
    """
    Object to control serial port functionality.
    """

    def __init__(self, name, port):
        """
        Initializes the Port object

        Args:
            name: String ID for serial port 
            port: USB connection for Arduino in '/dev/tty*'
            manager: A Manager() dict object passed through by config.py
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
        try:
            self.radio = Module.get_instance(self)  # Initialize radio communication
        except Exception as e:
            print(e)
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

    def JSONpass(self, manager):
        """
        Overwrites dict with sensor data and sends over radio

        Args:
            manager: A Manager() dict object passed through by config.py
        """
        self.writeDict()
        manager = self.json    # Add json to Manager() to pass to comm_parse
        try:
            self.radio.send(json.dumps(self.json))  # Send json over radio
        except Exception as e:
            print(e)

    def speedTest(self, dur):
        """
        Tests the speed of data acquisition from Arduino for a given time.

        Args:
            dur: duration (in seconds) of test
        """
        start = time.time()
        i = 0
        while time.time() < start + dur:
            self.writeDict()
            i = i + 1
        print("\nPolling rate: {} Hz\n".format(i / dur))
