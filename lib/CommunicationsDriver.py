#! /usr/bin/python3.6
import json

from orbitalcoms import (
    create_serial_launch_station
) 

#from Radio import Radio
class Comm:
    __instance = None

    def __init__(self, DEBUG, port, baudrate):
        if Comm.__instance is not None:
            raise Exception("Constructor should not be called")
        else:
            Comm.__instance = CommSingleton(DEBUG, port, baudrate)

    def get_instance(self, DEBUG, port, baudrate):
        if Comm.__instance is None:
            print("first")
            Comm(DEBUG, port, baudrate)
        else: print("not first")
        return Comm.__instance


class CommSingleton:
    def __init__(self, DEBUG = 0, port='/dev/ttyuUSB0', baudrate=9600):
        try:
            self.__radio = create_serial_launch_station(port, baudrate)
            self.__arm = False
            print(self.__radio)
        except Exception as e:
            print("EXCEPTION CAUGHT")
            print(e)
            
    def send(self, command):

        try:
            if not len(command) == 0:
                print(command)
                self.__radio.send(json.dumps(command))
        except Exception as e:
            print(e)

    def bind(self, queue):
        self.__radio.bindQueue(queue)

    def getLaunchFlag(self):
        return self.__radio.getLaunchFlag()
    
    def getQDMFlag(self):
        return self.__radio.getQDMFlag()
    
    def getAbortFlag(self):
        return self.__radio.getAbortFlag()
        
    def getStabFlag(self):
        return self.__radio.getStabFlag()

    @property
    def arm(self):
        return self.__arm
      
    @arm.setter
    def arm(self, arm):
        self.__arm = arm

