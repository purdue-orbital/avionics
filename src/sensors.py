import sys, os
import json
import time
from threading import Thread, Event
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
        radio_port : if not None, port of radio for ground station communication
                            else, radio isn't used
    """

    class Function:
        """
        List node for functions to be called
        Arguments:
            name : function name to be called
            freq : frequency with which to call function
            id   : string for json key
            token: column header for logging purposes
            args : any arguments to the function
        """
        def __init__(self, name, freq, identity, token, args):
            self.name = name
            self.freq = freq
            self.id = identity
            self.token = token
            self.args = args
            self.next = None

    class SLL:
        """
        Method to reference head node and prepend a node
        """
        def __init__(self):
            self.head = None
        
        def add(self, node):
            if node.id is not None:  # Initialize sensors
                node.name(node.args)

            node.next = self.head
            self.head = node

    class IntThread(Thread):
        def __init__(self, obj):
            Thread.__init__(self, daemon=True)
            self.trigger = Event()
            self.obj = obj

        def run(self):
            while not self.trigger.wait(1 / self.obj.freq):
                if self.obj.args is not None: self.obj.name(self.obj.args)
                else: self.obj.name()
            
    def __init__(self, name, imu_address=0x69, radio_port=None):
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
                      "GPS": {
                        "long": 0,
                        "lat": 0,
                        "alt": 0
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

        # Initialize sensor Modules
        try: self.clock = DS3231("DS3231", clock_pin)
        except:
            self.console.warning("DS3231 not initialized")
            self.clock = None
            self.start_time = time.time()
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
        """
        Specify cleanup procedure. Protects against most crashes
        """
        if exc_type is not None: self.console.critical(f"{exc_type.__name__}: {exc_value}")
        GPIO.cleanup()
        self.log.close()
    
    def launch_detect(self, callback):
        """
        Callback function for the rocket_in pin
        """
        logging.info(f"Launch detected at mission time {self.time[0]}")

    def write_header(self):
        """
        Writes header for specified sensors to log file
        """
        head = self.list.head
        string = []

        while head is not None:
            if head.token is not None:  # Any data-writing function will have a token
                string.append(head.token)
            head = head.next

        self.log.write(",".join(string) + "\n")
        
    def write(self):
        """
        Writes specified sensors to log file
        """
        head = self.list.head
        string = []
        
        while head is not None:
            if head.token is not None:  # Any data-writing function will have a token
                data = head.name()
                if head.id is not None:  # If data is being sent over radio, will have an ID
                    sub = self.json[head.id]
                    if type(data) is dict:
                        sub = {list(sub.keys())[i]: data[i] for i in range(len(data))}
                    else:  # case of temperature, only has one variable
                        sub = data[0]
                string.append(",".join([str(x) for x in data]))
            head = head.next

        self.log.write(",".join(string) + "\n")

    def print(self):
        """
        Prints most recent data collected for debugging
        """
        head = self.list.head
        string = []
        
        while head is not None:
            if head.id is not None:
                string.append(",".join([str(x) for x in head.name()]))
            head = head.next

        print(",".join(string))

    def pass_to(self, manager, *args):
        """
        Writes most recent data to a shared dictionary w/ command thread

        Args:
            manager: A Manager() dictionary object passed through by balloon.py
            *args: head name of data to be passed
        """
        # This is straight up cancerous, but the way dict management works between
        # processes requires the dictionary to be reassigned to notify the DictProxy
        # of changes to itself
        temp = manager[0]
        temp = {k: v for k, v in self.json.items() if k in args} # Prune keys
        # Reassign here
        manager[0] = temp

    def send(self):
        """
        Sends most recent data collected over radio
        """
        self.c.send(self.json, "balloon")

    def add(self, name, freq, identity=None, token=None, args=None):
        """
        Calls inner function SLL.add(node)
        Arguments:
            name: function name to be called
            freq: frequency with which to call function
            args: any arguments to the function
        """
        self.list.add(self.Function(name, freq, identity, token, args))

    @property
    def least(self):
        """
        Finds least frequently polled sensor
        """
        head = self.list.head
        min = head.freq
        
        while head is not None:
            if (head.freq < min): min = head.freq
            head = head.next

        return min

    @property
    def greatest(self):
        """
        Finds most frequently polled sensor
        """
        head = self.list.head
        max = head.freq
        
        while head is not None:
            if (head.freq > max): max = head.freq
            head = head.next

        return max

    def stitch(self):
        """
        Runs all desired sensors at desired frequency
        Arguments:
            head: Function() object which is first sensor in list
        """
        head = self.list.head

        while head is not None:
            # print(f"Spawning thread {head.name.__name__} with frequency {head.freq} Hz...")
            self.console.info(f"Spawning thread {head.name.__name__} with frequency {head.freq} Hz...")
            t = self.IntThread(head)
            t.start()
            
            head = head.next

    def time(self):
        """
        Reads time from the DS3231 RTC
        """
        if self.clock is not None:
            return (self.clock.time,)
        else: return (time.time() - self.start_time,)

    def gps(self, *args):
        """
        Reads positional GPS data from the NEO7M chip
        """
        if not args: return self._gps
        elif (args[0][0] == "w"):
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
        elif (args[0][0] == "w"):
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
        elif (args[0][0] == "w"):
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
        elif (args[0][0] == "w"):
            try:
                self._magnet = self.ak.mag
            except Exception as e:
                self.console.error(e)
                self._magnet = (-999, -999, -999)
        
    def temperature(self, *args):
        """
        Reads temperature data from the MS5611 chip
        """
        if not args: return (self._temperature,)
        elif (args[0][0] == "w"):
            try:
                self._temperature = self.clock.temp
            except Exception as e:
                self.console.error(e)
                self._temperature = (-999,)
                
    def speed_test(self, duration, function, *args):
        """
        Tests the speed of data acquisition from a function for a given time.
        Arguments:
            duration: duration (in seconds) of test
        """
        start = self.time[0]
        i = 0

        while self.time[0] < start + duration:
            function(*args)
            i = i + 1
        print("\nPolling rate: {} Hz\n".format(i / duration))


if __name__ == "__main__":
    with Sensors("balloon") as sensors:
        # Launch thread in write mode so it doesn't just read
        sensors.add(sensors.temperature, 1, identity="temp", token="temp (C)", args=["w"])
        # sensors.add(sensors.gps, 0.5, identity="GPS", token="lat, long, alt (m)", args=["w"])
        sensors.add(sensors.accel, 1, identity="acc", token="ax (g),ay (g),az (g)", args=["w"])
        sensors.add(sensors.gyro, 2, identity="gyro", token="gx (dps),gy (dps),gz (dps)", args=["w"])
        
        ### DON'T CHANGE ###
        sensors.add(sensors.time, sensors.greatest, token="time (s)")
        sensors.write_header()
        sensors.add(sensors.write, sensors.greatest)
        sensors.stitch()
        # time.sleep(2 * sensors.least)
        ### DON'T CHANGE ###
        
        while True:
            sensors.print()
            time.sleep(1)
