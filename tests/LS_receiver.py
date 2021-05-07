

from RadioBeta import Radio
import _thread as thread
import json
import time

gsradio = Radio(1, True)

queue = []

gsradio.bindQueue(queue)

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