import os, sys
import _thread as thread
import json
import time
from datetime import datetime, timedelta

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join('..', 'logs')))
sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
sys.path.append(os.path.abspath(os.path.join('..', 'src')))

#from Radio import Radio
from RadioBeta import Radio
from CommunicationsDriver import Comm
from sensors import Sensors
lsradio = Radio(1)   

def recv():
    queue = []
    lsradio.bindQueue(queue)

    while True:
        try:
            print(len(queue))
            if len(queue) > 0:
                print("Popping....")
                print(queue.pop(0))
            else:
                print("Queue Empty")
        except Exception as e:
            print(e)
        
        time.sleep(1)

thread.start_new_thread(recv,())


with Sensors("balloon") as sensors:
    # Lambda used to pass generic multi-arg functions to sensors.add
    # These will later be executed in unique threads
    sensors.add(lambda: sensors.temperature(write=True), 1, identity="temp",
        token="temp (C)", access=lambda: sensors.temperature()
    )

    sensors.add(lambda: sensors.gps(write=True), 0.5, identity="GPS",
        token="lat, long, alt (m)", access=lambda: sensors.gps()
    )

    sensors.add(lambda: sensors.accel(write=True), 100, identity="acc",
        token="ax (g),ay (g),az (g)", access=lambda: sensors.accel()
    )

    sensors.add(lambda: sensors.gyro(write=True), 100, identity="gyro",
        token="gx (dps),gy (dps),gz (dps)", access=lambda: sensors.gyro()
    )

    sensors.add(lambda: sensors.send(), 1)

    
    ### DON'T CHANGE ###
    sensors.add(lambda: sensors.time(), sensors.greatest, token="time (s)")
    sensors.write_header()
    sensors.add(lambda: sensors.write(), sensors.greatest)
    sensors.stitch()
    ### DON'T CHANGE ###
    
    while True:
        time.sleep(1)

