from datetime import datetime, timedelta
from RadioModule import Module
import json
from math import atan, pi
import RPi.GPIO as GPIO
import time
from array import *
import os
import queue

class Control:

    def __init__(self,qdmpin,ignitionpin,error):
        self.radio = Module.get_instance(self)
        
        self.qdmpin = qdmpin
        self.ignitionpin = ignitionpin
        
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(qdmpin,GPIO.OUT)
        GPIO.setup(ignitionpin,GPIO.OUT)
        
        self.error = error
        
        self.balloon = None
        self.rocket = None
        
        self.commands = queue.Queue(maxsize = 10)
        
        
    def QDMCheck(self, QDM):
        '''
        This checks if we need to QDM.
        Parameter: QDM
        
        if QDM = 0, QDM initiated
        else, do nothing
        
        return void
        '''
                
        if (QDM == 1):
            GPIO.output(self.qdmpin,True)
        else:
            GPIO.output(self.qdmpin,False)
            self.radio.send(json.dumps({"QDM":"Activated"}))
        
        return 0


    def Ignition(self, mode):
        '''
        This checks condition and starts ignition
        Parameters: - mode: test mode or pre-launch mode
                    - datarange: compare data btw two computers
                    - datain: data from sensors
        
        test mode: flow current for 3 sec
        pre-launch mode: flow current for 10 sec
        
        return void
        '''
        
        
        
        Launch = self.LaunchCondition()
        if Launch:
            if (mode == 1):
                #class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
                GPIO.output(self.ignitionpin,True)
                self.radio.send(json.dumps({"Ignition":"Activated"}))
                time.sleep(0.1)
                #class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(True), pin_factory(None))
                GPIO.output(self.ignitionpin,False)
            elif (mode == 2):
                #class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
                GPIO.output(self.ignitionpin,True)
                self.radio.send(json.dumps({"Ignition":"Activated"}))
                time.sleep(10)
                #class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(True), pin_factory(None))
                GPIO.output(self.ignitionpin,False)
                

        return 0


    def readdata(self, rocket,balloon):

        '''
        This reads the data from sensors and check whether they are within range of 5%
        Parameters: - datain: data from sensors
        
        compare condition of rocket and ballon and check if their difference has percent error less than 5 %
        
        return result - condition within range or not
        '''
        
        
            
        ROCKET_LONG = rocket['GPS']['long']
        ROCKET_LATI = rocket['GPS']['lat']

        ROCKET_ALT = rocket['alt']

        ROCKET_GYRO_X = rocket['gyro']['x']
        ROCKET_GYRO_Y = rocket['gyro']['y']
        ROCKET_GYRO_Z = rocket['gyro']['z']


        ROCKET_MAGNET_X = rocket['mag']['x']
        ROCKET_MAGNET_Y = rocket['mag']['y']
        ROCKET_MAGNET_Z = rocket['mag']['z']
        
        ROCKET_TEMP = rocket['temp']

        ROCKET_ACC_X = rocket['acc']['x']
        ROCKET_ACC_Y = rocket['acc']['y']
        ROCKET_ACC_Z = rocket['acc']['z']

        self.rocket = [ROCKET_ALT,ROCKET_LONG,ROCKET_LATI,ROCKET_GYRO_X,ROCKET_GYRO_Y,ROCKET_GYRO_Z,ROCKET_MAGNET_X,ROCKET_MAGNET_Y,ROCKET_MAGNET_Z,ROCKET_TEMP,ROCKET_ACC_X,ROCKET_ACC_Y,ROCKET_ACC_Z]

        BAL_LONG = balloon['GPS']['long']
        BAL_LATI = balloon['GPS']['lat']

        BAL_ALT = balloon['alt']

        BAL_GYRO_X = balloon['gyro']['x']
        BAL_GYRO_Y = balloon['gyro']['y']
        BAL_GYRO_Z = balloon['gyro']['z']
        
        BAL_MAGNET_X = balloon['mag']['x']
        BAL_MAGNET_Y = balloon['mag']['y']
        BAL_MAGNET_Z = balloon['mag']['z']

        BAL_TEMP = balloon['temp']

        BAL_ACC_X = balloon['acc']['x']
        BAL_ACC_Y = balloon['acc']['y']
        BAL_ACC_Z = balloon['acc']['z']


        self.balloon = [BAL_ALT,BAL_LONG,BAL_LATI,BAL_GYRO_X,BAL_GYRO_Y,BAL_GYRO_Z,BAL_MAGNET_X,BAL_MAGNET_Y,BAL_MAGNET_Z,BAL_TEMP,BAL_ACC_X,BAL_ACC_Y,BAL_ACC_Z]

    def dataerrorcheck(self):
        result = False
        
        for i in range (0,12,1):
            rangecheck = abs(self.rocket[i]-self.balloon[i]) / self.rocket[i]
            
            if (rangecheck > self.error):
                result = False
                break
            else:
                result = True
        
        return result



    def LaunchCondition(self):
        '''
        This check Launch condition
        
        return result: launch condition true or false

        '''
        
        
        altitude = (self.balloon[0]<=25500) & (self.balloon[0] >= 24500)
        spinrate = (self.balloon[3]<=5) & (self.balloon[4]<=5) & (self.balloon[5]<=5)
        degree = atan(self.balloon[7]/self.balloon[6]) * 180/pi
        direction = (degree <= 100) & (degree >= 80)
            
        return (altitude & spinrate & direction)



    def ConnectionCheck(self):

        connected = os.path.isfile('./receive/[groundstation].json')
            
        return connected

    def receivedata(self):
        self.commands.put(json.loads(self.radio.receive()))
        if not self.commands.empty():
            return self.commands.get()
