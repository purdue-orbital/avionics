import os, sys
import _thread as thread
import json
import time

sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from RadioBeta import Radio

lsradio = Radio(1)
time.sleep(1)
gsradio = Radio(1, True)


def recv():
    queue = []

    lsradio.bindQueue(queue)

    while True: 
        try:
            print(len(queue))
            if len(queue) > 0:
                print("Popping...")
                print(queue.pop(0))
            else:
                print("Queue empty")
        except Exception as e:
            print(e)


        time.sleep(1)


thread.start_new_thread(recv, ())

time.sleep(3)   

jsonData = {}
jsonData['QDM'] = False
jsonData['LAUNCH'] = True
jsonData['ABORT'] = False
jsonData['STAB'] = False
gsradio.send(json.dumps(jsonData))

time.sleep(3)
