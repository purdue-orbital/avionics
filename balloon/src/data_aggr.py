import sys, os
import serial
import json
import pynmea2

# Import modules from ../lib and add ../logs to PATH
sys.path.append(os.path.abspath(os.path.join('..', 'logs')))
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))

from CommunicationsDriver import Comm
from mpu9 import mpu9250
from ds32 import DS3231

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
                      "mag": 0,
                      "temp": 0,
                      "acc": {
                        "x": 0,
                        "y": 0,
                        "z": 0
                      }
                    }

        # Open log file and write header
        self.log = open('../logs/data.log', 'a+')

        # Write header
        self.log.write(
            'time (s),alt (m),lat,long,a_x (g),a_y (g),a_z (g),g_x (dps),g_y (dps),g_z (dps),m_x (mT),m_y (mT),'
            'm_z (mT),temp (C)\n')

        self.c = Comm.get_instance()
        self.clock = DS3231("DS3231", clock_pin)              # Create DS3231 Object from ds32.py
        self.imu = mpu9250(mpu_address=imu_address)           # Create mpu9250 Object from mpu9.py
        self.neo = serial.Serial(gps_port, 9600, timeout=0.5) # Create Serial Object for the NEO 7M GPS

        self.last = (0, 'N', 0, 'E', 0)
        
        if radio_port is not None:  # Create radio object if desired
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

        self.c.send(self.json, "balloon")

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
        t = self.clock.time
        
        print(
            "{:.3f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(
                t, alt, lat, lon, ax, ay, az, gx, gy, gz, mx, my, mz, temp))

    def speed_test(self, dur):
        """
        Tests the speed of data acquisition from sensors for a given time.

        Args:
            dur: duration (in seconds) of test
        """
        start = self.clock.time
        i = 0

        while self.clock.time < start + dur:
            self.readAll()
            i = i + 1
        print("\nPolling rate: {} Hz\n".format(i / dur))

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
            self.magnet = self.imu.mag
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

    @property
    def gps(self):
        """
        Reads GPS data from the NEO7M chip
        """
        string = self.neo.readline().decode('utf-8')
        
        if (string.find('GGA') > 0):
            msg = pynmea2.parse(string)

            # Uncomment to print
            # if False:
            #     print("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s" % (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units))

            if msg.lat != '':
                self.gps = (msg.lat, msg.lat_dir, msg.lon, msg.lon_dir, msg.altitude)
            else:
                self.gps = (-999, 'ERR', -999, 'ERR', -999)
            return self._gps

    @gps.setter
    def gps(self, values):
        self._gps = values


if __name__ == "__main__":
    print("Running data_aggr.py ...\n")
    sens = Sensors("Balloon Computer")

    while True:
        sens.read_all()
        sens.printd()
