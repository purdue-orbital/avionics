from datetime import datetime, timedelta
from RadioModule import Module
import json
from math import atan, pi
import RPi.GPIO as GPIO
import time
from array import *
import os


def QDMCheck(QDM):
    '''
    This checks if we need to QDM.
    Parameter: QDM
    
    if QDM = 0, QDM initiated
    else, do nothing
    
    return void
    '''

    GPIO.setmode(GPIO.BCM)
    Outputsignal = 6
    GPIO.setup(Outputsignal,GPIO.OUT)
    
    if (QDM == 1):
        GPIO.output(Outputsignal,True)
    else:
        GPIO.output(Outputsignal,False)
    
    return 0


def Ignition(datain,mode,datarange):
    '''
    This checks condition and starts ignition
    Parameters: - mode: test mode or pre-launch mode
                - datarange: compare data btw two computers
                - datain: data from sensors
    
    test mode: flow current for 3 sec
    pre-launch mode: flow current for 10 sec
    
    return void
    '''
    GPIO.setmode(GPIO.BCM)
    Outputsignal = 5
    GPIO.setup(Outputsignal,GPIO.OUT)
    
    
    
    if datarange:
        Launch = LaunchCondition(datain)
        if Launch:
            if (mode == 1):
                #class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
                GPIO.output(Outputsignal,True)
                time.sleep(3)
                #class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(True), pin_factory(None))
                GPIO.output(Outputsignal,False)
            elif (mode == 2):
                #class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
                GPIO.output(Outputsignal,True)
                time.sleep(10)
                #class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(True), pin_factory(None))
                GPIO.output(Outputsignal,False)
            
    GPIO.cleanup()

    return 0


def DataErrorCheck(rocket,balloon):

    '''
    This reads the data from sensors and check whether they are within range of 5%
    Parameters: - datain: data from sensors
    
    compare condition of rocket and ballon and check if their difference has percent error less than 5 %
    
    return result - condition within range or not
    '''
    
    
    #array[altitude,logitude,latitude,gyro_x,gyro_y,gyro_z,mag_x,mag_y,temp,acc_x,acc_y,acc_z]
        
    ROCKET_LONG = rocket['GPS']['long']
    ROCKET_LATI = rocket['GPS']['lat']

    ROCKET_ALT = rocket['alt']

    ROCKET_GYRO_X = rocket['gyro']['x']
    ROCKET_GYRO_Y = rocket['gyro']['y']
    ROCKET_GYRO_Z = rocket['gyro']['z']

    #ROCKET_MAGNET_X = rocket['mag']

    ROCKET_MAGNET_X = rocket['mag']['x']
    ROCKET_MAGNET_Y = rocket['mag']['y']
    ROCKET_MAGNET_Z = rocket['mag']['z']
    
    ROCKET_TEMP = rocket['temp']

    ROCKET_ACC_X = rocket['acc']['x']
    ROCKET_ACC_Y = rocket['acc']['y']
    ROCKET_ACC_Z = rocket['acc']['z']

    Rocket = [ROCKET_ALT,ROCKET_LONG,ROCKET_LATI,ROCKET_GYRO_X,ROCKET_GYRO_Y,ROCKET_GYRO_Z,ROCKET_MAGNET_X,ROCKET_MAGNET_Y,ROCKET_MAGNET_Z,ROCKET_TEMP,ROCKET_ACC_X,ROCKET_ACC_Y,ROCKET_ACC_Z]
#    Rocket = [ROCKET_ALT,ROCKET_LONG,ROCKET_LATI,ROCKET_GYRO_X,ROCKET_GYRO_Y,ROCKET_GYRO_Z,ROCKET_MAGNET_X,ROCKET_TEMP,ROCKET_ACC_X,ROCKET_ACC_Y,ROCKET_ACC_Z]

    BAL_LONG = balloon['GPS']['long']
    BAL_LATI = balloon['GPS']['lat']

    BAL_ALT = balloon['alt']

    BAL_GYRO_X = balloon['gyro']['x']
    BAL_GYRO_Y = balloon['gyro']['y']
    BAL_GYRO_Z = balloon['gyro']['z']

#    BAL_MAGNET_X = balloon['mag']
    
    BAL_MAGNET_X = balloon['mag']['x']
    BAL_MAGNET_Y = balloon['mag']['y']
    BAL_MAGNET_Z = balloon['mag']['z']

    BAL_TEMP = balloon['temp']

    BAL_ACC_X = balloon['acc']['x']
    BAL_ACC_Y = balloon['acc']['y']
    BAL_ACC_Z = balloon['acc']['z']


    Balloon = [BAL_ALT,BAL_LONG,BAL_LATI,BAL_GYRO_X,BAL_GYRO_Y,BAL_GYRO_Z,BAL_MAGNET_X,BAL_MAGNET_Y,BAL_MAGNET_Z,BAL_TEMP,BAL_ACC_X,BAL_ACC_Y,BAL_ACC_Z]
#    Balloon = [BAL_ALT,BAL_LONG,BAL_LATI,BAL_GYRO_X,BAL_GYRO_Y,BAL_GYRO_Z,BAL_MAGNET_X,BAL_TEMP,BAL_ACC_X,BAL_ACC_Y,BAL_ACC_Z]

    result = False
    
    for i in range (0,12,1):
        rangecheck = abs(Rocket[i]-Balloon[i]) / Rocket[i]
        
        if (rangecheck > 0.05):
#            print('data off range')
            result = False
            break
        else:
#            print('data within range')
            result = True
    
    return result



def LaunchCondition(balloon):
    '''
    This check Launch condition
    
    return result: launch condition true or false

    '''
    BAL_ALT = balloon['alt']

    BAL_GYRO_X = balloon['gyro']['x']
    BAL_GYRO_Y = balloon['gyro']['y']
    BAL_GYRO_Z = balloon['gyro']['z']

#    BAL_MAGNET_X = balloon['mag']
#    BAL_MAGNET_Y = balloon['mag']
    
    BAL_MAGNET_X = balloon['mag']['x']
    BAL_MAGNET_Y = balloon['mag']['y']
    #BAL_MAGNET_Z = balloon['mag']['z']

    
    altitude = (BAL_ALT<=25500) & (BAL_ALT >= 24500)
    spinrate = (BAL_GYRO_X<=5) & (BAL_GYRO_Y<=5) & (BAL_GYRO_Z<=5)
    degree = atan(BAL_MAGNET_Y/BAL_MAGNET_X) * 180/pi
    direction = (degree <= 100) & (degree >= 80)
    
    
    result = False
    
    
    if (altitude == False):
#        print('altitude off range')
        result = False
    elif (spinrate == False):
#        print('spinrate off range')
        result = False
    elif (direction == False):
#        print('direction off range')
        result = False
    else:
#        print('launch condition true')
        result = True
        
    return result



def ConnectionCheck():

    connected = os.path.isfile('./receive/[groundstation].json')
    if (connected):
        print('connection true')
        return 1
    else:
        print('connection false')
        return 0
        
    return False



if __name__ == "__main__":

    result = ConnectionCheck()
    endT = datetime.now() + timedelta(seconds = 10)
    while ((result == 0) & (datetime.now() < endT)):
        result = ConnectionCheck()
    if (result == 0):
        QDMCheck(0)
    else:
        with open('./receive/[groundstation].json') as gsin:
            GSDATA = json.load(gsin)
    
        QDM = GSDATA['QDM']
        IGNITION = GSDATA['Ignition']
        #    CDM = GSDATA['CDM']
        #    STAB = GSDATA['Stabilization']
        #    CRASH = GSDATA['Crash']
        #    DROGUE = GSDATA['Drogue']
        #    MAIN_CHUTE = GSDATA['Main_Chute']

        QDMCheck(QDM)

        with open('./send/rocket.json') as R:
            rocket = json.load(R)
        with open('./send/balloon.json') as B:
            balloon = json.load(B)

        condition = DataErrorCheck(rocket,balloon)
        mode = 1
        if ((condition == True) & (IGNITION == 1)):
            Ignition(balloon,mode,condition)
