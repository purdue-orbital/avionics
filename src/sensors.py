import sys, os
import json
import time
import threading
import logging
import RPi.GPIO as GPIO

# Import modules from ../lib and add ../logs to PATH
os.chdir(os.path.dirname(os.path.abspath(__file__)))
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
    Arguments:
        name       : String ID for sensor package
        imu_address: i2c address of MPU9250 and MS5611
        gps_port   : Port of serial object GPS NEO 7M
        radio_port : if not None, port of radio for ground station communication
                            else, radio isn't used
        clock_pin  : GPIO pin the SQW line from the DS3231 is connected to
    """

    class Function:
        """
        List node for functions to be called
        Arguments:
            name: function name to be called
            freq: frequency with which to call function
            args: any arguments to the function
        """
        def __init__(self, name, freq, args):
            self.name = name
            self.freq = freq
            self.args = args
            self.next = None

    class SLL:
        """
        Method to reference head node and prepend a node
        """
        def __init__(self):
            self.head = None
        
        def add(self, node):
            node.next = self.head
            self.head = node

    def __init__(self, name, imu_address=0x69, gps_port='/dev/ttyAMA0', radio_port=None):
        # Set up debug logging
        self.console = logging.getLogger('sensors')
        _format = "%(asctime)s %(threadName)s %(levelname)s > %(message)s"
        logging.basicConfig(
            level=logging.INFO, filename='../logs/status_sensors.log', filemode='a+', format=_format
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
                      "origin": name,
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

        self.list = self.SLL()

        # GPIO.output(23, GPIO.HIGH)
        # time.sleep(2)
        # GPIO.output(23, GPIO.LOW)
        
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
        
    def write(self):
        """
        Writes specified sensors to log file
        """
        head = self.list.head
        string = []
        
        while head is not None:
            string.append(",".join([str(x) for x in head.name()]))
            head = head.next

        self.log.write(",".join(string) + "\n")

    def print(self):
        """
        Prints most recent data collected for debugging
        """
        head = self.list.head
        string = []
        
        while head is not None:
            string.append(",".join([str(x) for x in head.name()]))
            head = head.next

        print(",".join(string))

    def pass_to(self, manager):
        """
        Writes most recent data to a shared dictionary w/ command thread

        Args:
            manager: A Manager() dictionary object passed through by balloon.py
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
        # Assigning each sensor value required to dictionary
        
        self.json["GPS"]["lat"], self.json["GPS"]["long"], self.json["alt"] = self.gps
        self.json["gyro"]["x"], self.json["gyro"]["y"], self.json["gyro"]["z"] = self.gyro
        self.json["mag"]["x"], self.json["mag"]["y"], self.json["mag"]["z"] = self.magnet
        self.json["acc"]["x"], self.json["acc"]["y"], self.json["acc"]["z"] = self.accel
        self.json["temp"] = self.temperature

        self.c.send(self.json, "balloon")

    def add(self, name, freq, args=None):
        """
        Calls inner function SLL.add(node)
        Arguments:
            name: function name to be called
            freq: frequency with which to call function
            args: any arguments to the function
        """
        self.list.add(self.Function(name, freq, args))

    @property
    def least(self):
        """
        Finds least frequently polled sensor
        """
        head = self.list.head
        max = head.freq
        
        while head is not None:
            if (head.freq > max): max = head.freq
            head = head.next

        return max

    def caller(self, function, hz, *args, **kwargs):
        """
        Calls a function at a defined frequency (used for polling).
        Arguments:
            function: function you want to call
            hz: frequency (in Hz) to call function
            *args: any arguments you want passed to the function
            **kwargs: keyword arguments you want passed to the function
        """
        start = self.clock.time
        print(start)
        while True:
            if (self.clock.time > (start + 1/hz)):
                print("Enter %f", self.clock.time)
                function(*args, **kwargs)
                start = self.clock.time
            else: time.sleep(1/hz)

    def stitch(self):
        """
        Runs all desired sensors at desired frequency
        Arguments:
            head: Function() object which is first sensor in list
        """
        head = self.list.head

        while head is not None:
            if head.args is not None:
                t = threading.Timer(head.freq, head.name, args=head.args)
            else: t = threading.Timer(head.freq, head.name)

            t.daemon = True
            t.start()
            head = head.next

    def gps(self, *args):
        """
        Reads positional GPS data from the NEO7M chip
        """
        if not args: return self._gps
        elif (args[0] == "w"):
            try:
                self._gps = self.neo.position
            except Exception as e:
                self.console.error(e)
                self._gps = (-999, -999, -999)
        
    def accel(self, *args):
        """
        Reads acceleration from the MPU9250 chip
        """
        if not args: return self._accel
        elif (args[0] == "w"):
            try:
                self._accel = self.imu.accel
            except Exception as e:
                self.console.error(e)
                self._accel = (-999, -999, -999)

    def gyro(self, *args):
        """
        Reads gyroscopic data from the MPU9250 chip
        """
        if not args: return self._gyro
        elif (args[0] == "w"):
            try:
                self._gyro = self.imu.gyro
            except Exception as e:
                self.console.error(e)
                self._gyro = (-999, -999, -999)
                
    def magnet(self, *args):
        """
        Read magnetometer data from the MPU9250 chip
        """
        if not args: return self._magnet
        elif (args[0] == "w"):
            try:
                self._magnet = self.ak.mag
            except Exception as e:
                self.console.error(e)
                self._magnet = (-999, -999, -999)
        
    def temperature(self, *args):
        """
        Reads temperature data from the MS5611 chip
        """
        if not args: return self._temperature
        elif (args[0] == "w"):
            try:
                self._temperature = self.clock.temp
            except Exception as e:
                self.console.error(e)
                self._temperature = -999
                
    def speed_test(self, dur):
        """
        Tests the speed of data acquisition from sensors for a given time.
        Arguments:
            dur: duration (in seconds) of test
        """
        start = self.clock.time
        i = 0

        while self.clock.time < start + dur:
            self.write()
            i = i + 1
        print("\nPolling rate: {} Hz\n".format(i / dur))


if __name__ == "__main__":
    print("Running sensors.py ...\n")

    with Sensors("balloon") as sensors:
        # Launch thread in write mode so it doesn't just read
        sensors.add(sensors.temperature, 1, "w")
        sensors.add(sensors.gyro, 1, "w")
        print(type(sensors.temperature))
        sensors.add(sensors.gps, 0.5, "w")
        sensors.stitch()

        print(sensors.least)
        time.sleep(2 * sensors.least)
        
        while True:
            sensors.write()
            sensors.print()
            
            time.sleep(1)
