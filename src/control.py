import sys, os
import time
import json, math
import queue
import logging
from math import atan, pi
import RPi.GPIO as GPIO
from array import *

sys.path.append(os.path.abspath(os.path.join('..', 'lib')))

from RadioModule import Module
from CommunicationsDriver import Comm


class Control:

    @staticmethod
    def generate_status_json():
        json = {}
        json["origin"] = "status"
        json["QDM"] = 0
        json["Ignition"] = 0
        json["Stabilization"] = 0
        return json

    def __init__(self, qdmpin, ignitionpin, rocketlogpin, stabilizationpin):
        self.qdmpin = qdmpin
        self.ignitionpin = ignitionpin
        self.rocketlogpin = rocketlogpin
        self.stabilizationpin = stabilizationpin

        self.gyro_queue = queue.Queue(maxsize=100)

        # GPIO SETUP
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(qdmpin,GPIO.OUT)
        GPIO.setup(ignitionpin,GPIO.OUT)
        GPIO.setup(rocketlogpin,GPIO.OUT)
        GPIO.output(rocketlogpin,True)
        GPIO.setup(stabilizationpin,GPIO.OUT)

        self.balloon = None
        # self.rocket = None

        self.c = Comm.get_instance()

        self.commands = queue.Queue(maxsize=10)

        # Set up info logging
        self.console = logging.getLogger('control')
        _format = "%(asctime)s %(threadName)s %(levelname)s > %(message)s"
        logging.basicConfig(
            level=logging.INFO, filename='avionics/src/status_control.py', filemode='a', format=_format
        )

    def qdm_check(self, QDM):
        '''
        This checks if we need to QDM.
        Parameter: QDM

        if QDM = 0, QDM initiated
        else, do nothing

        return void
        '''

        if QDM == 1:
            GPIO.output(self.qdmpin,True)
        else:
            GPIO.output(self.qdmpin,False)

            data = self.generate_status_json()
            data["QDM"] = 1
            self.c.send(data, "status")
            logging.info("QDM initiated")

        return 0

    def ignition(self, mode):
        '''
        This checks condition and starts ignition
        Parameters: - mode: test mode or pre-launch mode
                    - datarange: compare data btw two computers
                    - datain: data from sensors

        test mode: flow current for 3 sec
        pre-launch mode: flow current for 10 sec

        return void
        '''

        launch = self.launch_condition()
        if launch:
            if (mode == 1):
                # class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
                GPIO.output(self.ignitionpin,True)
                data = Control.generate_status_json()
                data["Ignition"] = 1
                self.c.send(data, "status")
                time.sleep(0.1)
                # class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(True), pin_factory(None))
                GPIO.output(self.ignitionpin,False)
                logging.info("Rocket ignition (testing)")

            elif (mode == 2):
                GPIO.output(self.rocketlogpin,False)
                time.sleep(5)  # tell rocket to start logging and give appropriate time
                # class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
                GPIO.output(self.ignitionpin,True)
                data = Control.generate_status_json()
                data["Ignition"] = 1
                self.c.send(data, "status")
                time.sleep(10)
                # class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(True), pin_factory(None))
                GPIO.output(self.ignitionpin,False)
                logging.info("Rocket ignition")

        return 0

    def read_data(self, balloon):

        '''
        This reads the data from sensors and checks whether they are within range of 5%
        Parameters: - datain: data from sensors

        compare condition of rocket and ballon and check if their difference has percent error less than 5 %

        return none
        '''
        alt = balloon['GPS']['alt']

        gx = balloon['gyro']['x']
        gy = balloon['gyro']['y']
        gz = balloon['gyro']['z']

        if (self.gyro_queue.full()): 
            self.gyro_queue.get()
            
        self.gyro_queue.put([gx, gy, gz])

        self.balloon = [alt, gx, gy, gz]
        logging.debug("Data received")

    def lowpass_gyro(self, tolerance):
        """
        Implements a low-pass filter to accurately determine spinrate,
        and returns True if within spec.

        Arguments:
            tolerance : spec (in dps) to allow for
        """
        gx, gy, gz = self.gyro_queue.get()

        return (math.sqrt(gx**2 + gy**2 + gz**2) < tolerance)

    def launch_condition(self):
        '''
        Returns True if both spinrate and altitude are within spec.

        return result: launch condition true or false
        '''

        altitude = (self.balloon[0]<=25500) & (self.balloon[0] >= 24500)
        spinrate = self.lowpass_gyro(5)
        logging.info(f"Altitude: {altitude} - Spinrate: {spinrate}")

        return (altitude & spinrate)

    def connection_check(self):
        return self.c.remote_device

    def stabilization(self):
        condition = (self.balloon[0]<=25500) & (self.balloon[0] >= 24500)
        if (condition):
            GPIO.output(self.stabilizationpin, GPIO.HIGH)
            data = self.generate_status_json()
            data["Stabilization"] = 1
            self.c.send(data,"status")
            logging.info("Stabilization initiated")

    def receive_data(self):
        self.commands.put(json.loads(self.c.receive()))
