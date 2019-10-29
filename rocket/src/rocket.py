import sys, os
import serial
import json
import pynmea2

# Import add ../logs/ and ../lib/ to PATH
sys.path.append(os.path.abspath(os.path.join('..', 'logs')))
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))

from mpu9 import mpu9250
from ds32 import DS3231

class Sensors:
    """
    Object-oriented approach to creating sensor functionality for
    IMU, GPS, RTC, and radio
    """

    def __init__(self, name, imu_address=0x69, gps_port='/dev/ttyAMA0', clock_pin=17):
        """
        Initializes the Sensors object

        Args:
            name       : String ID for sensor package
            imu_address: i2c address of MPU9250 and MS5611
            gps_port   : Port of serial object GPS NEO 7M
            clock_pin  : GPIO pin the SQW wire of DS3231 is connected to
        """

        print("Initializing {}...".format(name))
        self.name = name

        # Open log file and write header
        self.log = open('../logs/data.log', 'a+')
        self.log.write('time (s),alt (m),lat,long,a_x (g),a_y (g),a_z (g),g_x (dps),g_y (dps),g_z (dps),m_x (mT),m_y (mT),m_z (mT),temp (C)\n')
        
        self.clock = DS3231(clock_pin)                        # Create DS3231 Object from ds32.py
        self.imu = mpu9250(mpu_address=imu_address)           # Create mpu9250 Object from mpu9.py
        self.gps = serial.Serial(gps_port, 9600, timeout=0.5) # Create Serial Object for the NEO 7M GPS

        self.last = (0, 'N', 0, 'E', 0)
                        
        print("Initialization complete.\n")

        
    def read_all(self, printing=False):
        """
        Reads from sensors and writes to log file
        """

        gx, gy, gz = self.read_gyro()    # works, but negative numbers overflow to 250 dps
        mx, my, mz = self.read_magnet()  # gets data, but is garbage
        self.read_GPS()                  # works, with occasional SerialException: device reports readiness to read
        lat, _, lon, _, alt = self.last
        ax, ay, az = self.read_accel()   # works (uncalibrated)
        temp = self.read_temperature()   # works (uncalibrated)
        t = self.clock.time
            
        # Write to .log file
        self.log.write("{:.3f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(t,alt,lat,lon,ax,ay,az,gx,gy,gz,mx,my,mz,temp))

        if printing:
            print("{:.3f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(t,alt,lat,lon,ax,ay,az,gx,gy,gz,mx,my,mz,temp))

            
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

        
    def read_accel(self):
        """
        Reads acceleration from the MPU9250 chip
        """
        try:
            return self.imu.accel
        except OSError:
            return (-999, -999, -999)

        
    def read_gyro(self):
        """
        Reads gyroscopic data from the MPU9250 chip
        """
        try:
            return self.imu.gyro
        except OSError:
            return (-999, -999, -999)

        
    def read_magnet(self):
        """
        Read magnetometer data from the MPU9250 chip
        """
        try:
            return self.imu.mag
        except OSError:
            return (-999, -999, -999)

        
    def read_temperature(self):
        """
        Reads temperature data from the MS5611 chip
        """
        try:
            return self.imu.temp
        except OSError:
            return -999

        
    def read_GPS(self, printing=False):
        """
        Reads GPS data from the NEO7M chip
        """
        string = self.gps.readline().decode('utf-8')
        
        if (string.find('GGA') > 0):
            msg = pynmea2.parse(string)

            if printing:
                print("Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s" % (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units))

            if msg.lat != '':
                self.last = (msg.lat, msg.lat_dir, msg.lon, msg.lon_dir, msg.altitude)
            else:
                self.last = (-999, 'ERR', -999, 'ERR', -999)

                
if __name__ == "__main__":
    print("Running data_aggr.py ...\n")
    
    sens = Sensors("MPU9250")

    while True:
        sens.read_all()
