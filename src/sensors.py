
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

ROCKET_IN = 27

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
            perform : function call to execute generically
            access  : separate function call to read, if necessary
            freq : frequency with which to call function
            id   : string for json key
            token: column header for logging purposes
        """
        def __init__(self, perform, access, freq, identity, token):
            self.perform = perform
            if access is None: self.access = perform
            else: self.access = access

            self.freq = freq
            self.id = identity
            self.token = token
            self.next = None

    class SLL:
        """
        Method to reference head node and prepend a node
        """
        def __init__(self):
            self.head = None

        def add(self, node):
            if node.id is not None:  # Initialize sensors
                node.perform()

            node.next = self.head
            self.head = node

    class IntThread(Thread):
        """
        Spawn a Thread to repeat at a given interval
        Arguments:
            obj : a Function object to be executed
        """
        def __init__(self, obj):
            Thread.__init__(self, daemon=True)
            # Could be used to prematurely stop thread using self.trigger.set()
            self.trigger = Event()
            self.obj = obj

        def run(self):
            while not self.trigger.wait(1 / self.obj.freq):
                self.obj.perform()

    def __init__(self, name, imu_address=0x69, radio_port=True):
        # Set up debug logging
        self.console = logging.getLogger('sensors')
        _format = "%(asctime)s %(threadName)s %(levelname)s > %(message)s"
        logging.basicConfig(
            level=logging.INFO, filename='../logs/status_sensors.log', filemode='a+', format=_format
        )

        self.console.info(f"\n\n### Starting {name} ###\n")

        #on init, setup the rocket input pin and its event handler
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(ROCKET_IN, GPIO.IN)
        GPIO.add_event_detect(ROCKET_IN, GPIO.FALLING, self.launch_detect)

        self.name = name
        self.json = {
                      "origin": "balloon",
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
        try: self.clock = DS3231("DS3231")
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

        if radio_port is not None:  # Create radio object if desired
            try:
                #self.c = Comm.get_instance(self, 1, "127.0.0.1")  # Initialize radio communication
                self.c = Comm.get_instance(self)  # Initialize radio communication
                print("Sensors Attempting Radio Connection")
                time.sleep(5)
            except Exception as e:
                self.console.error(e)
        else:
            self.c = None
            self.console.warning("Radio not initialized")

        self.console.info("Initialization complete")

    #TODO: Change c.send to sending to the queue
    def send(self):
       self.c.send(self.json)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Specify cleanup procedure. Protects against most crashes
        """
        if exc_type is not None: self.console.critical(f"{exc_type.__name__}: {exc_value}")
        else: self.console.info("Sensors.py completed successfully.")
        GPIO.cleanup()
        self.log.close()

    def launch_detect(self, callback):
        """
        Callback function for the ROCKET_IN pin
        """
        logging.info(f"Launch detected at mission time {self.time()[0]}")
        GPIO.remove_event_detect(ROCKET_IN)

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
                data = head.access()
                if head.id is not None:  # If data is being sent over radio, will have an ID
                    sub = self.json[head.id]
                    if type(sub) is dict:
                        self.json[head.id] = {list(sub.keys())[i]: data[i] for i in range(len(data))}
                    else:  # case of temperature, only has one variable
                        self.json[head.id] = data[0]
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
            if head.token is not None:  # Anything with a header
                string.append(",".join([str(x) for x in head.access()]))
            head = head.next

        #print(",".join(string))

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
        # temp = {k: v for k, v in self.json.items() if k in args} # Prune keys
        # temp["time"] = self.time()[0]
        temp = self.json
        # Reassign here
        manager[0] = temp

    def add(self, perform, freq, identity=None, token=None, access=None):
        """
        Calls inner function SLL.add(node)
        Arguments:
            name: function name to be called
            freq: frequency with which to call function
            args: any arguments to the function
        """
        self.list.add(self.Function(perform, access, freq, identity, token))

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
            self.console.info(f"Spawning thread {head.id} with frequency {head.freq} Hz...")
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

    def gps(self, write=False):
        """
        Reads positional GPS data from the NEO7M chip
        """
        if write:
            try:
                self._gps = self.neo.position
            except Exception as e:
                self.console.error(e)
                self._gps = (-999, -999, -999)
        else: return self._gps

    def accel(self, write=False):
        """
        Reads acceleration from the MPU9250 chip
        """
        if write:
            try:
                self._accel = self.imu.accel
            except Exception as e:
                self.console.error(e)
                self._accel = (-999, -999, -999)
        else: return self._accel

    def gyro(self, write=False):
        """
        Reads gyroscopic data from the MPU9250 chip
        """
        if write:
            try:
                self._gyro = self.imu.gyro
            except Exception as e:
                self.console.error(e)
                self._gyro = (-999, -999, -999)
        else: return self._gyro

    def magnet(self, write=False):
        """
        Read magnetometer data from the MPU9250 chip
        """
        if write:
            try:
                self._magnet = self.ak.mag
            except Exception as e:
                self.console.error(e)
                self._magnet = (-999, -999, -999)
        else: return self._magnet

    def temperature(self, write=False):
        """
        Reads temperature data from the MS5611 chip
        """
        if write:
            try:
                self._temperature = (self.clock.temp,)
            except Exception as e:
                self.console.error(e)
                self._temperature = (-999,)
        else: return self._temperature

    def bind_queue(self, queue):
        self.communciation_queue = queue

if __name__ == "__main__":
    with Sensors("balloon", radio_port="true") as sensors:

        # Lambda used to pass generic multi-arg functions to sensors.add
        # These will later be executed in unique threads
        sensors.add(lambda: sensors.temperature(write=True), 1, identity="temp",
            token="temp (C)", access=lambda: sensors.temperature()
        )

        sensors.add(lambda: sensors.gps(write=True), 0.5, identity="GPS",
            token="lat, long, alt (m)", access=lambda: sensors.gps()
        )

        sensors.add(lambda: sensors.accel(write=True), 1, identity="acc",
            token="ax (g),ay (g),az (g)", access=lambda: sensors.accel()
        )

        sensors.add(lambda: sensors.gyro(write=True), 2, identity="gyro",
            token="gx (dps),gy (dps),gz (dps)", access=lambda: sensors.gyro()
        )

        # sensors.add(lambda:sensors.pass_to(temp), 1)
        sensors.add(lambda: sensors.print(), 1)
        sensors.add(lambda: sensors.send(), 1)

        ### DON'T CHANGE ###
        sensors.add(lambda: sensors.time(), sensors.greatest, token="time (s)")
        sensors.write_header()
        sensors.add(lambda: sensors.write(), sensors.greatest)
        sensors.stitch()
        ### DON'T CHANGE ###

        while True:
            time.sleep(1)
