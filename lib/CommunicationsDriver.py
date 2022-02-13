#! /usr/bin/python3.6
import json

from orbitalcoms import create_serial_launch_station

# from Radio import Radio
class Comm:
    __instance = None

    def __init__(self, port, baudrate):
        if self.__instance is not None:
            raise Exception("Constructor should not be called")
        else:
            self.__instance = CommSingleton(port, baudrate)

    @classmethod
    def get_instance(cls, port, baudrate):
        if cls.__instance is None:
            print("first")
            cls(port, baudrate)
        else:
            print("not first")
        return cls.__instance


class CommSingleton:
    def __init__(self, port="/dev/ttyuUSB0", baudrate=9600):
        try:
            self.__radio = create_serial_launch_station(port, baudrate)
            self.__arm = False
            print(self.__radio)
        except Exception as e:
            print("EXCEPTION CAUGHT")
            print(e)

    def send(self, command):
        print(f"Sending: {command}")
        if not self.__radio.send(json.dumps(command)):
            print("Message failed to send")

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
