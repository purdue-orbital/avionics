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
            level=logging.INFO, filename='avionics/src/control.py', filemode='a', format=_format
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
                data = self.generate_status_json(self)
                data["Ignition"] = 1
                self.c.send(data, "status")
                time.sleep(0.1)
                # class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(True), pin_factory(None))
                GPIO.output(self.rocketlogpin,False)
                GPIO.output(self.ignitionpin,False)
                logging.info("Rocket ignition (testing)")
            elif (mode == 2):
                # class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
                GPIO.output(self.ignitionpin,True)
                data = self.generate_status_json(self)
                data["Ignition"] = 1
                self.c.send(data, "status")
                time.sleep(10)
                # class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(True), pin_factory(None))
                GPIO.output(self.rocketlogpin,False)
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
        alt = balloon['alt']

        gx = balloon['gyro']['x']
        gy = balloon['gyro']['y']
        gz = balloon['gyro']['z']

        if (self.gyro_queue.full()): 
            self.gyro_queue.get()
            
        self.gyro_queue.put([gx, gy, gz])

        self.balloon = [alt, gx, gy, gz]
        logging.debug("Data received")

    def launch_condition(self):
        '''
        This check Launch condition

        return result: launch condition true or false
        '''

        altitude = (self.balloon[0]<=25500) & (self.balloon[0] >= 24500)
        spinrate = (math.sqrt(self.balloon[3]**2 + self.balloon[4]**2 + self.balloon[5]**2) <= 5)
        logging.info(f"Altitude: {altitude} - Spinrate: {spinrate}")

        return (altitude & spinrate)

    def connection_check(self):
        return self.radio.remote_device

    def stabilization(self,manager):
        self.read_data(manager)
        condition = (self.balloon[0]<=25500) & (self.balloon[0] >= 24500)
        if (condition):
            GPIO.output(self.stabilizationpin,True)
            data = self.generate_status_json()
            data["Stabilization"] = 1
            self.c.send(data,"status")
            logging.info("Stabilization initiated")

    def receive_data(self):
        self.commands.put(json.loads(self.c.receive()))
