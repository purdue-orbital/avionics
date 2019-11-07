import sys, os
import time
import json
import queue
from math import atan, pi
import RPi.GPIO as GPIO
from array import *

sys.path.append(os.path.abspath(os.path.join('..'. 'lib')))

from RadioModule import Module
from CommunicationsDriver import Comm

class Control:


    @staticmethod
    def generate_status_json(self):
        json = {}
        json["origin"] = "status"
        json["QDM"] = 0
        json["Ignition"] = 0
        json["Stabilization"] = 0
        return json

    def __init__(self,qdmpin,ignitionpin,stabilizationpin,error):
        self.radio = Module.get_instance(self)
        
        self.qdmpin = qdmpin
        self.ignitionpin = ignitionpin
        self.stabilizationpin = stabilizationpin
        
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(qdmpin,GPIO.OUT)
        GPIO.setup(ignitionpin,GPIO.OUT)
        GPIO.setup(stabilizationpin,GPIO.OUT)

        self.error = error
        
        self.balloon = None
        #self.rocket = None

        self.c = self.Comm.get_instance()

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


            data = self.generate_status_json()
            data["QDM"] = 1
            self.c.send(data, "status")
            #self.radio.send(json.dumps({"QDM":"Activated"}))
            

        return 0


    def Ignition(self, mode,manager):
        '''
        This checks condition and starts ignition
        Parameters: - mode: test mode or pre-launch mode
                    - datarange: compare data btw two computers
                    - datain: data from sensors
        
        test mode: flow current for 3 sec
        pre-launch mode: flow current for 10 sec
        
        return void
        '''
        
        
        self.readdata(manager)
        Launch = self.LaunchCondition()
        if Launch:
            if (mode == 1):
                #class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
                GPIO.output(self.ignitionpin,True)
                data = self.generate_status_json(self)
                data["Ignition"] = 1
                self.c.send(data, "status")
                #self.radio.send(json.dumps({"Ignition":"Activated"}))
                time.sleep(0.1)
                #class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(True), pin_factory(None))
                GPIO.output(self.ignitionpin,False)
            elif (mode == 2):
                #class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
                GPIO.output(self.ignitionpin,True)
                data = self.generate_status_json(self)
                data["Ignition"] = 1
                self.c.send(data,"status")
                #self.radio.send(json.dumps({"Ignition":"Activated"}))
                time.sleep(10)
                #class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(True), pin_factory(None))
                GPIO.output(self.ignitionpin,False)
                

        return 0


    def readdata(self, manager):

        '''
        This reads the data from sensors and check whether they are within range of 5%
        Parameters: - datain: data from sensors
        
        compare condition of rocket and ballon and check if their difference has percent error less than 5 %
        
        return none
        '''
            
        balloon = manager[0]

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

        connected = self.radio.remote_device
            
        return connected

    def receivedata(self)
        #if self.radio is not None:
        self.commands.put(json.loads(self.radio.queue.get()))

    def Stabilization(self,manager):
        self.readdata(manager)
        condition = (self.balloon[0]<=25500) & (self.balloon[0] >= 24500)
        if (condition):
            GPIO.output(self.stabilizationpin,True)
            data = self.generate_status_json(self)
            data["Stabilization"] = 1
            self.c.send(data,"status")

