#! /usr/bin/python3.6
import json

from orbitalcoms import create_socket_launch_station

# from Radio import Radio
class Comm:
    __instance = None

    def __init__(self, DEBUG, hostname):
        if Comm.__instance is not None:
            raise Exception("Constructor should not be called")
        else:
            Comm.__instance = CommSingleton(DEBUG, hostname)

    def get_instance(self, DEBUG, hostname):
        if Comm.__instance is None:
            print("first")
            Comm(DEBUG, hostname)
        else:
            print("not first")
        return Comm.__instance


class CommSingleton:
    def __init__(self, DEBUG=0, hostname="127.0.0.1"):
        try:
            self.__radio = create_socket_launch_station(hostname, 5000)
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
