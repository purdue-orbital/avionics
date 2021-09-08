import os, sys
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from RadioBeta import Radio
import _thread as thread
import json
import time

gsradio = Radio(1, True)

def recv():
    queue = []

    gsradio.bindQueue(queue)

    while True: 
        try:
            if len(queue) > 0:
                print(queue.pop(0))
        except Exception as e:
            print(e)


        time.sleep(1)


thread.start_new_thread(recv, ())


while(True):
    command = input("Type STABILITY, QDM, ABORT, LAUNCH: ")

    if command == "STABILITY":
        jsonData = {}
        jsonData['QDM'] = False
        jsonData['LAUNCH'] = False
        jsonData['ABORT'] = False
        jsonData['STAB'] = True
        gsradio.send(json.dumps(jsonData))
    elif command == "QDM":
        jsonData = {}
        jsonData['QDM'] = True
        jsonData['LAUNCH'] = False
        jsonData['ABORT'] = False
        jsonData['STAB'] = False
        gsradio.send(json.dumps(jsonData))
    elif command == "ABORT":
        jsonData = {}
        jsonData['QDM'] = False
        jsonData['LAUNCH'] = False
        jsonData['ABORT'] = True
        jsonData['STAB'] = False
        gsradio.send(json.dumps(jsonData))
    elif command == "LAUNCH":
        jsonData = {}
        jsonData['QDM'] = False
        jsonData['LAUNCH'] = True
        jsonData['ABORT'] = False
        jsonData['STAB'] = False
        gsradio.send(json.dumps(jsonData))
