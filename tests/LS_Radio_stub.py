import os, sys
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
from RadioBeta import Radio
import _thread as thread
import json
import time

lsradio = Radio(1)
queue = []
lsradio.bindQueue(queue)

while True: 
    try:
        if len(queue) > 0:
            print(queue.pop(0))
    except Exception as e:
        print(e)


    time.sleep(1)
