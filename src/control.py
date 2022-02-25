import logging
import math
import time

from collections import deque
from datetime import datetime, timedelta
from typing import Deque, Dict, List, Tuple

from orbitalcoms import ComsMessage

from CommunicationsDriver import Comm
from devutils import envvartobool

if envvartobool("ORBIT_MOCK_GPIO"):
    import mockGPIO as GPIO
else:
    import RPi.GPIO as GPIO


QDM_PIN = 13
IGNITION_PIN = 6
IGNITION_DETECTION_PIN = 25
ROCKET_LOG_PIN = 22
STABILIZATION_PIN = 21
POWER_ON_ALARM = 20  # minutes
# RIPD_PIN = 29


# Set up info logging
logging.basicConfig(
    level=logging.INFO,
    filename="../logs/status_control.log",
    filemode="a+",
    format="%(asctime)s %(processName)s::%(threadName)s %(levelname)s > %(message)s",
)
logger = logging.getLogger("control")


class Control:
    def __init__(self, name):
        logger.info(f"\n\n### Starting {name} ###\n")

        # Create a data queue
        self.gyro_queue: Deque[Tuple[float, float, float, float]] = deque()

        # GPIO SETUP
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(QDM_PIN, GPIO.OUT)
        GPIO.output(QDM_PIN, GPIO.HIGH)  # Turn on QDM dead switch
        GPIO.setup(IGNITION_PIN, GPIO.OUT)
        GPIO.setup(ROCKET_LOG_PIN, GPIO.OUT)
        GPIO.output(ROCKET_LOG_PIN, GPIO.HIGH)
        GPIO.setup(STABILIZATION_PIN, GPIO.OUT)
        GPIO.setup(IGNITION_DETECTION_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.altitude = None
        # self.rocket = None

        time.sleep(2)
        try:
            # Initialize radio communication
            self.comm_driver = Comm.get_instance(port="/dev/ttyUSB0", baudrate=9600)
            print("Control Attempting Radio Connection")
            time.sleep(5)
        except Exception as e:
            print(e)
        # self.commands = queue.Queue(maxsize=10)
        self.commands: List[ComsMessage] = []
        self.comm_driver.bind(self.commands)
        self.data = None

        # on start switch
        # self.endT = datetime.now() + timedelta(minutes=POWER_ON_ALARM)  #
        self.endT = datetime.now() + timedelta(hours=3)  #
        logger.info(f"POWER ON ALARM: {POWER_ON_ALARM} minutes")
        self.ground_abort = 0
        logger.info("Initialization complete")

    def generate_status_json(self) -> Dict[str, bool]:
        return {
            "LAUNCH": self.comm_driver.getLaunchFlag(),
            "QDM": self.comm_driver.getQDMFlag(),
            "ABORT": self.comm_driver.getAbortFlag(),
            "STAB": self.comm_driver.getStabFlag(),
            "ARMED": self.comm_driver.getArmedFlag(),
        }

    def set_end_time(self):
        self.endT = datetime.now() + timedelta(minutes=POWER_ON_ALARM)  #

    def groundAbort(self, abort=0):
        if abort:
            self.ground_abort = 1
        return self.ground_abort

    def safetyTimer(self):
        if (datetime.now() > self.endT) and (not self.ground_abort):
            print("safety_timer")
            self.qdm_check(1)

    def get_next_msg(self) -> ComsMessage:
        return self.commands.pop(0)

    def getLaunchFlag(self) -> bool:
        return self.comm_driver.getLaunchFlag()

    def getQDMFlag(self) -> bool:
        return self.comm_driver.getQDMFlag()

    def getAbortFlag(self) -> bool:
        return self.comm_driver.getAbortFlag()

    def getStabFlag(self) -> bool:
        return self.comm_driver.getStabFlag()

    def is_armed(self):
        return self.comm_driver.getArmedFlag()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Specify cleanup procedure. Protects against most crashes
        """
        print("EXITED CONTROL")
        if exc_type is not None:
            logger.critical(f"{exc_type.__name__}: {exc_value}")
        else:
            logger.info("Control.py completed successfully.")
        GPIO.cleanup()

    def read_data(self, proxy):
        """
        Reads data from Manager.list() given by sensors.py

        Arguments:
            proxy : list containing dict and time
        """
        self.data = proxy[0]

        if self.data:
            self.send()  # send data over radio

            self.altitude = self.data["GPS"]["alt"]
            gx = self.data["gyro"]["x"]
            gy = self.data["gyro"]["y"]
            gz = self.data["gyro"]["z"]
            # time = balloon['time']

            if len(self.gyro_queue) > 100:
                # FIXME: Pops at over 100 but only last 10 points ever used
                self.gyro_queue.popleft()

            self.gyro_queue.append((time.time(), gx, gy, gz))
            logging.debug("Data received")

    def send(self) -> None:
        """
        Sends most recent data collected over radio
        """
        if self.data:
            message = self.generate_status_json()
            message["DATA"] = self.data
            self.comm_driver.send(message)

    def lowpass_gyro(self) -> float:
        """
        TODO
        Implements a low-pass filter to accurately determine and return spinrate
        magnitude
        """
        gx, gy, gz = 0, 0, 0

        if len(self.gyro_queue) > 10:
            for i in range(1, 11):
                _, gx_, gy_, gz_ = self.gyro_queue[-i]
                gx += gx_ / 10
                gy += gy_ / 10
                gz += gz_ / 10
        elif len(self.gyro_queue):
            gx, gy, gz = self.gyro_queue[-1]

        return math.sqrt(gx**2 + gy**2 + gz**2)

    def launch_condition(self) -> None:
        """
        Returns True if both spinrate and altitude are within spec.
        FIXME: docstring has incorrect info

        return result: launch condition true or false
        """
        spinrate = self.lowpass_gyro()
        logging.info(f"Altitude: {self.altitude}m - Spinrate: {spinrate}dps")

    def stabilization(self):
        """
        Checks ability to stabilize, dependent on altitude. Sends update to
        ground station with action taken.
        """
        logging.info("Stabilization attempted")
        # Bounds hard-coded for "ease" of manipulation (not worth the effort)
        # condition = (self.altitude<=25500) & (self.altitude >= 24500)
        condition = True
        if condition:
            GPIO.output(STABILIZATION_PIN, GPIO.HIGH)
            print("stabilization")
            logging.info("Stabilization initiated")
        else:
            # FIXME: Unreachable code block
            logging.error(
                f"Stabilization failed: altitude {self.altitude}m not within bounds"
            )

    def ignition(self, mode):
        """
        This checks condition and starts ignition
        Parameters: - mode: test mode or pre-launch mode
                    - datarange: compare data btw two computers
                    - datain: data from sensors

        test mode: flow current for 0.1 sec
        pre-launch mode: flow current for 10 sec

        return void
        """
        logging.info("Ignition attempted")
        data = self.generate_status_json()

        # launch = self.launch_condition()
        launch = True
        if launch:
            data["Ignition"] = 1
            GPIO.add_event_detect(IGNITION_DETECTION_PIN, GPIO.RISING)
            if mode == 1:  # testing mode (avoid igniting motor)
                GPIO.output(IGNITION_PIN, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(IGNITION_PIN, GPIO.LOW)
                logging.info("Ignition initiated (testing)")
                if GPIO.event_detected(IGNITION_DETECTION_PIN):
                    logging.info("Ignition (testing) detected")
                else:
                    logging.warn("Ignition(testing) not detected")

            elif mode == 2:  # Ignite motor
                print("Igniting Motor")
                GPIO.output(ROCKET_LOG_PIN, GPIO.LOW)
                time.sleep(5)  # tell rocket to start logging and give appropriate time
                print("ign out")
                GPIO.output(IGNITION_PIN, GPIO.HIGH)
                time.sleep(10)  # Needs to be experimentally verified
                GPIO.output(IGNITION_PIN, GPIO.LOW)
                logging.info("Ignition initiated")
                if GPIO.event_detected(IGNITION_DETECTION_PIN):
                    logging.info("Ignition detected")
                else:
                    logging.warn("IGNITION not detected")

        else:
            logging.error(
                "Ignition failed: altitude and/or spinrate not within tolerance"
            )

    def abort(self) -> None:
        logging.info("aborted")
        print("Aborting")
        GPIO.cleanup()

    def qdm_check(self, QDM: bool) -> None:
        """
        This checks if we need to QDM.
        Parameter: QDM

        if QDM = 0, QDM initiated
        else, do nothing

        return void
        """

        if QDM:
            GPIO.output(QDM_PIN, GPIO.LOW)
            data = self.generate_status_json()
            data["QDM"] = True
            logging.info("QDM initiated")
        else:
            GPIO.output(QDM_PIN, GPIO.HIGH)

    def is_queued_msgs(self) -> bool:
        return bool(self.commands)


if __name__ == "__main__":
    """
    Controls all command processes for the balloon flight computer.
    """

    print("Running control.py ...\n")

    with Control("balloon") as ctrl:
        mode = 2  # mode 1 = testmode / mode 2 = pre-launch mode

        # collect = ctrl.Collection(lambda: ctrl.read_data(self.proxy), 1) #TODO if copying straight into balloon, uncomment 296 297
        # collect.start()
        while True:
            # Control loop to determine radio disconnection
            result = ctrl.is_queued_msgs()
            endT = datetime.now() + timedelta(
                seconds=5
            )  # Wait 5 seconds to reestablish signal TODO if copying straight into ballon, change to 500
            while (result == 0) & (datetime.now() < endT):
                result = ctrl.is_queued_msgs()
                time.sleep(0.5)  # Don't overload CPU

            # These don't need to be parallel to the radio connection, since we won't
            # be getting commands if the radio is down
            if result == 0:
                ctrl.qdm_check(0)
            else:
                # Receive commands and iterate through them
                if ctrl.getLaunchFlag():
                    ctrl.ignition(mode)
                if ctrl.getQDMFlag():
                    ctrl.qdm_check(0)
                if ctrl.getAbortFlag():
                    ctrl.abort()
                if ctrl.getStabFlag():
                    ctrl.stabilize()
