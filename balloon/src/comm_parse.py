import sys, os
import time
import json
import queue
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

    def __init__(self,qdmpin,ignitionpin,rocketlogpin,error):
        self.qdmpin = qdmpin
        self.ignitionpin = ignitionpin
	self.rocketlogpin = rocketlogpin
 
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(qdmpin,GPIO.OUT)
        GPIO.setup(ignitionpin,GPIO.OUT)
	GPIO.setup(rocketlogpin,GPIO.OUT)
        
	GPIO.output(rocketlogpin,True)

        self.error = error
        
        self.balloon = None
        self.rocket = None

        self.c = Comm.get_instance()
        
        self.commands = queue.Queue(maxsize=10)

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
            # self.radio.send(json.dumps({"QDM": "Activated"}))
        
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

        return 0

    def read_data(self, balloon):

        '''
        This reads the data from sensors and check whether they are within range of 5%
        Parameters: - datain: data from sensors
        
        compare condition of rocket and ballon and check if their difference has percent error less than 5 %
        
        return result - condition within range or not
        '''
        lon = balloon['GPS']['long']
        lat = balloon['GPS']['lat']

        alt = balloon['alt']

        gx = balloon['gyro']['x']
        gy = balloon['gyro']['y']
        gz = balloon['gyro']['z']
        
        mx = balloon['mag']['x']
        my = balloon['mag']['y']
        mz = balloon['mag']['z']

        temp = balloon['temp']

        ax = balloon['acc']['x']
        ay = balloon['acc']['y']
        az = balloon['acc']['z']

        self.balloon = [alt, lon, lat, gx, gy, gz, mx, my, mz, temp, ax, ay, az]

    def launch_condition(self):
        '''
        This check Launch condition
        
        return result: launch condition true or false

        '''
        
        altitude = (self.balloon[0]<=25500) & (self.balloon[0] >= 24500)
        spinrate = (self.balloon[3]<=5) & (self.balloon[4]<=5) & (self.balloon[5]<=5)
        degree = atan(self.balloon[7]/self.balloon[6]) * 180/pi
        direction = (degree <= 100) & (degree >= 80)
            
        return (altitude & spinrate & direction)

    def connection_check(self):
        return os.path.isfile('./receive/[groundstation].json')

    def receive_data(self):
        self.commands.put(json.loads(self.c.receive()))
        if not self.commands.empty():
            return self.commands.get()
