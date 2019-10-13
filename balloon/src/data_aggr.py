import serial
import json
import time
import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'logs')))

from _mpu9250 import mpu9250


# from RadioModule import Module

class Sensors():
    """
    Object to control serial port functionality.
    """

    def __init__(self, name):
        """
        Initializes the Port object

        Args:
            name: String ID for serial port 
            port: USB connection for Arduino in '/dev/tty*'
            manager: A Manager() dict object passed through by config.py
        """
        print("Initializing {}...".format(name))
        self.name = name
        self.json = {"Altitude": 0,   # Initialize dictionary structure
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

        # Open log file
        self.log = open('../logs/data.log', 'a+')
        # Write header
        self.log.write('time (s),alt (m),long,lat,g_x (dps),g_y (dps),g_z (dps),m_x (mT),m_y (mT),m_z (mT),temp (C),a_x (mg),a_y (mg),a_z (mg)\n')

        self.imu = mpu9250()  # Create IMU Object from mpu9250.py
        self.start = time.time()
        
        """
        try:
            self.radio = Module.get_instance(self)  # Initialize radio communication
        except Exception as e:
            print(e)
        """
        print("Initialization complete.\n")

    def writeDict(self):
        """
        Reads from Serial connection and writes to dict
        """

        gx, gy, gz = self.readGyro()
        mx, my, mz = self.readMagnet()      # works (uncalibrated)
        lat, lon, alt = self.readGPS()  # works (uncalibrated)
        ax, ay, az = self.readAccel() # works (uncalibrated)
        temp = self.readTemperature()             # works (uncalibrated)
        t = time.time() - self.start
        
        # Write to .log file
        self.log.write("{:.3f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(t,alt,lon,lat,gx,gy,gz,mx,my,mz,temp,ax,ay,az))
        
        # Assigning each value in given list to dict entry
        self.json["Altitude"] = alt
        self.json["GPS"]["longitude"] = lon
        self.json["GPS"]["latitude"] = lat
        self.json["Gyroscope"]["x"] = gx
        self.json["Gyroscope"]["y"] = gy
        self.json["Gyroscope"]["z"] = gz
        self.json["Magnetometer"]["x"] = mx
        self.json["Magnetometer"]["y"] = my
        self.json["Magnetometer"]["z"] = mz
        self.json["Temperature"] = temp
        self.json["Accelerometer"]["x"] = ax
        self.json["Accelerometer"]["y"] = ay
        self.json["Accelerometer"]["z"] = az

    def JSONpass(self, manager):
        """
        Overwrites dict with sensor data and sends over radio

        Args:
            manager: A Manager() dict object passed through by config.py
        """
        self.writeDict()

        # This is straight up cancerous, but the way dict management works between
        # processes requires the dict to be reassigned to notify the DictProxy
        # of changes to itself
        time.sleep(0.01)
        temp = manager[0]
        temp = self.json
        # Reassign here
        manager[0] = temp

        """
        try:
            self.radio.send(json.dumps(self.json))  # Send json over radio
        except Exception as e:
            print(e)
        """

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


    def readAccel(self):
        """
        Reads acceleration from the MPU9250 chip
        """
        return self.imu.accel

    def readGyro(self):
        """
        Reads gyroscopic data from the MPU9250 chip
        """
        return self.imu.gyro

    def readMagnet(self):
        """
        Read magnetometer data from the MPU9250 chip
        """
        return self.imu.mag

    def readTemperature(self):
        """
        Reads temperature data from the MS5611 chip
        """
        return self.imu.temp

    def readGPS(self):
        """
        Reads GPS data from the NEO7M chip
        """
        return (0, 0, 0)

if __name__ == "__main__":
    print("Running data_aggr.py ...\n")

    sens = Sensors("MPU9250")

    while True:
        sens.writeDict()
