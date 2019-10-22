#! /usr/bin/python3.6
import json

from Mode import Mode
from RadioModule import Module


class Comm:
    __instance = None

    def __init__(self):
        if Comm.__instance is not None:
            raise Exception("Constructor should not be called")
        else:
            Comm.__instance = CommSingleton()

    def get_instance(self):
        if Comm.__instance is None:
            Comm()
        return Comm.__instance


class CommSingleton:
    def __init__(self):
        self.__radio = Module.get_instance(self)

    def send(self, command):

        command_json = {}


        command_json["mode"] = "testing"
        command_json["command"] = command

        command_json["mode"] = "flight"
        command_json["command"] = command

        try:
            if not len(command_json) == 0:
                print(command_json)
                self.__radio.send(json.dumps(command_json))
        except Exception as e:
            print(e)
