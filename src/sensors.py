import sys, os
import json
import time
import threading
import logging
import RPi.GPIO as GPIO

# Import modules from ../lib and add ../logs to PATH
sys.path.append(os.path.abspath(os.path.join('..', 'logs')))
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))

# from CommunicationsDriver import Comm
from mpu9 import MPU9250
from ak89 import AK8963
from ds32 import DS3231
from neo7 import NEO7M

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
            clock_pin  : GPIO pin the SQW line from the DS3231 is connected to
        """

        self.console = logging.getLogger('data_aggregation')
        _format = "%(asctime)s %(threadName)s %(levelname)s > %(message)s"
        logging.basicConfig(
            level=logging.INFO, filename='../logs/status_data.log', filemode='a+', format=_format
        )

        self.console.info(f"\n\n### Starting {name} ###\n")

        rocket_in = 27
        clock_pin = 17

        #on init, setup the rocket input pin and its event handler
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(rocket_in, GPIO.IN)
        GPIO.setup(23, GPIO.OUT)
        GPIO.add_event_detect(rocket_in, GPIO.FALLING, self.launch_detect)
        
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
            'm_z (mT),temp (C)\n'
        )

        # Initialize sensor Modules
        try: self.clock = DS3231("DS3231", clock_pin)
        except:
            self.console.warning("DS3231 not initialized")
            self.clock = time
            self.console.info("Using system clock")
        try: self.imu = MPU9250("MPU9250", mpu_address=imu_address)
        except: self.console.warning("MPU9250 not initialized")
        try: self.ak = AK8963("AK8963")
        except: self.console.warning("AK8963 not initialized")
        try: self.neo = NEO7M()
        except: self.console.warning("NEO 7M GPS not initialized")

        GPIO.output(23, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(23, GPIO.LOW)
        
        self.gps = (0, 0)
        
        if radio_port is not None:  # Create radio object if desired
            try:
                self.c = Comm.get_instance(self)  # Initialize radio communication
            except Exception as e:
                self.console.error(e)
        else:
            self.c = None
            self.console.warning("Radio not initialized")

        self.console.info("Initialization complete")

    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None: self.console.critical(f"{exc_type.__name__}: {exc_value}")
        GPIO.cleanup()
    
    #callback function for the rocketIn pin
    def launch_detect(self, callback):
        logging.info(f"Launch detected at mission time {self.clock.time}")
        
    def read_all(self):
        """
        Reads from sensors and writes to log file
        """

        gx, gy, gz = self.gyro    # works, but negative numbers overflow to 250 dps
        mx, my, mz = self.magnet  # gets data, but is garbage
        lat, lon, alt = self.gps_position()
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
    
    def gps_position(self):
        """
        Reads positional GPS data from the NEO7M chip
        """
        return self.neo.position

    @property
    def accel(self):
        """
        Reads acceleration from the MPU9250 chip
        """
        try:
            self.accel = self.imu.accel
        except Exception as e:
            self.console.error(e)
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
        except Exception as e:
            self.console.error(e)
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
        except Exception as e:
            self.console.error(e)
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
        except Exception as e:
            self.console.error(e)
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
    sens = Sensors("Balloon Computer")

    with sens:
        while True:
            sens.read_all()
            sens.printd()
