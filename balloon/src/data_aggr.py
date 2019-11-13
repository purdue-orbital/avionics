import sys, os
import json
import time
import threading

# Import modules from ../lib and add ../logs to PATH
sys.path.append(os.path.abspath(os.path.join('..', 'logs')))
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))

from CommunicationsDriver import Comm
from mpu9 import MPU9250
from ak89 import AK8963
from ds32 import DS3231
from neo7 import NEO7M

class Sensors:
    """
    Object-oriented approach to creating sensor functionality for
    IMU, GPS, RTC, and radio
    """

    def __init__(self, name, imu_address=0x69, gps_port='/dev/ttyAMA0', radio_port=None, clock_pin=17):
        """
        Initializes the Sensors object

        Args:
            name       : String ID for sensor package
            imu_address: i2c address of MPU9250 and MS5611
            gps_port   : Port of serial object GPS NEO 7M
            radio_port : if not None, port of radio for ground station communication
                                else, radio isn't used
            clock_pin  : GPIO pin the SQW line from the DS3231 is connected to
        """

        print("Initializing {} sensors...".format(name))
        self.name = name
        self.json = {
                      "origin": "balloon",
                      "alt": 0,
                      "GPS": {
                        "long": 0,
                        "lat": 0
                      },
                      "gyro": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                      },
                      "mag": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                      },
                      "temp": 0,
                      "acc": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                      }
        }

        # Open log file and write header
        self.log = open('../logs/data.log', 'a+')
        self.log.write(
            'time (s),alt (m),lat,long,a_x (g),a_y (g),a_z (g),g_x (dps),g_y (dps),g_z (dps),m_x (mT),m_y (mT),'
            'm_z (mT),temp (C)\n')

        # Initialize sensor Modules
        self.clock = DS3231("DS3231", clock_pin)
        self.imu = MPU9250("MPU9250", mpu_address=imu_address)
        self.ak = AK8963("AK8963")
        self.neo = NEO7M(gps_port, 0.5)
        
        self._lock = threading.Lock() # Generate thread lock
        # Spawn GPS thread as daemon (will terminate at end of script)
        threading.Thread(target=self.gps_continuous_read, daemon=True)
        
        if radio_port is not None:  # Create radio object if desired
            try:
                self.c = Comm.get_instance(self)  # Initialize radio communication
            except Exception as e:
                print(e)
        else:
            self.c = None

        print("Initialization complete.\n")

    def read_all(self):
        """
        Reads from sensors and writes to log file
        """

        gx, gy, gz = self.gyro    # works, but negative numbers overflow to 250 dps
        mx, my, mz = self.magnet  # gets data, but is garbage
        lat, _, lon, _, alt = self.gps  # works, with occasional SerialException: device reports readiness to read
        ax, ay, az = self.accel   # works (uncalibrated)
        temp = self.temperature   # works (uncalibrated)
        t = self.clock.time

        # Write to .log file
        self.log.write(
            "{:.3f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(
                t, alt, lat, lon, ax, ay, az, gx, gy, gz, mx, my, mz, temp))

        # Assigning each value in given list to dictionary
        self.json["alt"] = alt
        self.json["GPS"]["long"] = lon
        self.json["GPS"]["lat"] = lat
        self.json["gyro"]["x"] = gx
        self.json["gyro"]["y"] = gy
        self.json["gyro"]["z"] = gz
        self.json["mag"]["x"] = mx
        self.json["mag"]["y"] = my
        self.json["mag"]["z"] = mz
        self.json["temp"] = temp
        self.json["acc"]["x"] = ax
        self.json["acc"]["y"] = ay
        self.json["acc"]["z"] = az

    def pass_to(self, manager):
        """
        Writes most recent data to a shared dictionary w/ command thread

        Args:
            manager: A Manager() dictionary object passed through by origin.py
        """
        # This is straight up cancerous, but the way dict management works between
        # processes requires the dictionary to be reassigned to notify the DictProxy
        # of changes to itself
        temp = manager[0]
        temp = self.json
        # Reassign here
        manager[0] = temp

    def send(self):
        """
        Sends most recent data collected over radio
        """

        self.c.send(self.json, "balloon")

    def printd(self):
        """
        Prints most recent data collected for debugging
        """

        alt = self.json["alt"]
        lon = self.json["GPS"]["long"]
        lat = self.json["GPS"]["lat"]
        gx = self.json["gyro"]["x"]
        gy = self.json["gyro"]["y"]
        gz = self.json["gyro"]["z"]
        mx = self.json["mag"]["x"]
        my = self.json["mag"]["y"]
        mz = self.json["mag"]["z"]
        temp = self.json["temp"]
        ax = self.json["acc"]["x"]
        ay = self.json["acc"]["y"]
        az = self.json["acc"]["z"]
        t = self.clock.time
        
        print(
            "{:.3f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(
                t, alt, lat, lon, ax, ay, az, gx, gy, gz, mx, my, mz, temp))
    
    def gps_continuous_read(self):
        """
        Reads GPS data from the NEO7M chip
        Continuous for implementation of thread
        """
        while True:
            try:
                data = self.neo.read()
                self.gps = data
            except OSError: # Connection error equates to -999 -- lethals
                self.gps = (-999, 'ERR', -999, 'ERR', -999)
            time.sleep(0.25)

    @property
    def accel(self):
        """
        Reads acceleration from the MPU9250 chip
        """
        try:
            self.accel = self.imu.accel
        except OSError:
            self.accel = (-999, -999, -999)
        return self._accel

    @accel.setter
    def accel(self, values):
        self._accel = values
            
    @property
    def gyro(self):
        """
        Reads gyroscopic data from the MPU9250 chip
        """
        try:
            self.gyro = self.imu.gyro
        except OSError:
            self.gyro = (-999, -999, -999)
        return self._gyro
    
    @gyro.setter
    def gyro(self, values):
        self._gyro = values
        
    @property
    def magnet(self):
        """
        Read magnetometer data from the MPU9250 chip
        """
        try:
            self.magnet = self.ak.mag
        except OSError:
            self.magnet = (-999, -999, -999)
        return self._magnet

    @magnet.setter
    def magnet(self, values):
        self._magnet = values

    @property
    def temperature(self):
        """
        Reads temperature data from the MS5611 chip
        """
        try:
            self.temperature = self.imu.temp
        except OSError:
            self.temperature = -999
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value
        
    def speed_test(self, dur):
        """
        Tests the speed of data acquisition from sensors for a given time.

        Args:
            dur: duration (in seconds) of test
        """
        start = self.clock.time
        i = 0

        while self.clock.time < start + dur:
            self.read_all()
            i = i + 1
        print("\nPolling rate: {} Hz\n".format(i / dur))


if __name__ == "__main__":
    print("Running data_aggr.py ...\n")
    sens = Sensors("Balloon Computer")

    while True:
        sens.read_all()
        sens.printd()
