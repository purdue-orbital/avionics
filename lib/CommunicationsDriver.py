#! /usr/bin/python3.6
import json

from Mode import Mode
from Radio import Radio 


class Comm:
    __instance = None

    def __init__(self):
        if Comm.__instance is not None:
            raise Exception("Constructor should not be called")
        else:
            Comm.__instance = CommSingleton()

    def get_instance(self):
        print("get called")
        if Comm.__instance is None:
            print("first")
            Comm()
        else: print("not first")
        return Comm.__instance


class CommSingleton:
    def __init__(self):
        try:
            self.__radio = Radio() 
        except Exception as e:
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
        self.__radio.getLaunchFlag()
    
    def getQDMFlag(self):
        self.__radio.getQDMFlag()
    
    def getAbortFlag(self):
        self.__radio.getAbortFlag()
