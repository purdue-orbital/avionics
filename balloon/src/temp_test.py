import time
import sys, os

from datetime import datetime
from mpu9 import mpu9250

imu = mpu9250()
temp = self.imu.temp()

sTime = datetime.now()
log = open('../logs/dataTemp.log', 'w+')    #Currently set to overwrite the current file for testing purposes. PLEASE CHANGE THIS TO a+ BEFORE YOU TEST!!
log.write('time (s) temp (C)\n')

for x in range(0,5):
    print(f'{datetime.now().second - sTime.second} {temp}')
    log.write(f'{datetime.now().second - sTime.second} {temp}\n')
    time.sleep(1)

