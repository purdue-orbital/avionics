import serial
import json
import time

import sys
import os

# Import modules from ../lib and add ../logs to PATH
sys.path.append(os.path.abspath(os.path.join('..', 'logs')))
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))

import mpu9250
from CommunicationsDriver import Comm


class Sensors:
    """
    Object-oriented approach to creating sensor functionality for
    IMU, GPS, RTC, and radio
    """

    def __init__(self, name, imu_address=0x69, gps_port='/dev/ttyAMA0', radio_port=None):
        """
        Initializes the Sensors object

        Args:
            name       : String ID for sensor package
            imu_address: i2c address of MPU9250 and MS5611
            gps_port   : Port of serial object GPS NEO 7M
            radio_port : if not None, port of radio for ground station communication
                                else, radio isn't used
        """

        print("Initializing {}...".format(name))
        self.name = name
        self.json = {"Altitude": 0,  # Initialize dictionary structure
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
        self.log.write(
            'time (s),alt (m),lat,long,a_x (g),a_y (g),a_z (g),g_x (dps),g_y (dps),g_z (dps),m_x (mT),m_y (mT),'
            'm_z (mT),temp (C)\n')

        self.imu = mpu9250(mpu_address=imu_address)  # Create IMU Object from mpu9250.py
        self.start = time.clock_gettime(time.CLOCK_REALTIME)  # Start time for logging purposes

        if radio_port is not None:
            try:
                self.radio = Module.get_instance(self)  # Initialize radio communication
            except Exception as e:
                print(e)

        else:
            self.radio = None

        print("Initialization complete.\n")

    def read_all(self):
        """
        Reads from sensors and writes to log file
        """

        gx, gy, gz = self.read_gyro()  # works, but has formatting/overflow errors
        mx, my, mz = self.read_magnet()  # gets data, but is garbage
        lat, lon, alt = self.read_gps()  # works (uncalibrated)
        ax, ay, az = self.read_accel()  # works (uncalibrated)
        temp = self.read_temperature()  # works (uncalibrated)
        t = time.clock_gettime(time.CLOCK_REALTIME) - self.start

        # Write to .log file
        self.log.write(
            "{:.3f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(
                t, alt, lat, lon, ax, ay, az, gx, gy, gz, mx, my, mz, temp))

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

    def pass_to(self, manager):
        """
        Writes most recent data to a shared dictionary w/ command thread

        Args:
            manager: A Manager() dict object passed through by origin.py
        """
        # This is straight up cancerous, but the way dict management works between
        # processes requires the dict to be reassigned to notify the DictProxy
        # of changes to itself
        time.sleep(0.01)
        temp = manager[0]
        temp = self.json
        # Reassign here
        manager[0] = temp

    def send(self):
        """
        Sends most recent data collected over radio
        """

        if self.radio is not None:
            try:
                self.radio.send(json.dumps(self.json))  # Send json over radio
            except Exception as e:
                print(e)

    def printd(self):
        """
        Prints most recent data collected for debugging
        """

        alt = self.json["Altitude"]
        lon = self.json["GPS"]["longitude"]
        lat = self.json["GPS"]["latitude"]
        gx = self.json["Gyroscope"]["x"]
        gy = self.json["Gyroscope"]["y"]
        gz = self.json["Gyroscope"]["z"]
        mx = self.json["Magnetometer"]["x"]
        my = self.json["Magnetometer"]["y"]
        mz = self.json["Magnetometer"]["z"]
        temp = self.json["Temperature"]
        ax = self.json["Accelerometer"]["x"]
        ay = self.json["Accelerometer"]["y"]
        az = self.json["Accelerometer"]["z"]
        t = time.clock_gettime(time.CLOCK_REALTIME) - self.start

        print(
            "{:.3f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(
                t, alt, lat, lon, ax, ay, az, gx, gy, gz, mx, my, mz, temp))

    def speed_test(self, dur):
        """
        Tests the speed of data acquisition from sensors for a given time.

        Args:
            dur: duration (in seconds) of test
        """
        start = time.time()
        i = 0
        while time.time() < start + dur:
            self.read_all()
            i = i + 1
        print("\nPolling rate: {} Hz\n".format(i / dur))

    def read_accel(self):
        """
        Reads acceleration from the MPU9250 chip
        """
        return self.imu.accel

    def read_gyro(self):
        """
        Reads gyroscopic data from the MPU9250 chip
        """
        return self.imu.gyro

    def read_magnet(self):
        """
        Read magnetometer data from the MPU9250 chip
        """
        return self.imu.mag

    def read_temperature(self):
        """
        Reads temperature data from the MS5611 chip
        """
        return self.imu.temp

    def read_gps(self):
        """
        Reads GPS data from the NEO7M chip
        """
        return 0, 0, 0


if __name__ == "__main__":
    print("Running data_aggr.py ...\n")
    print(f"The current time is {time.clock_gettime(time.CLOCK_REALTIME)}\n")

    sens = Sensors("MPU9250")

    while True:
        sens.read_all()
        sens.printd()
