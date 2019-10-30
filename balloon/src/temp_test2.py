import time
import datetime
import sys, os

sys.path.append(os.path.abspath(os.path.join('..','logs')))
sys.path.append(os.path.abspath(os.path.join('..','lib')))

from mpu9 import mpu9250
#from ds32 import DS3231

imu = mpu9250(mpu_address=0x69) # Sensor titled "CJMCU-MPU"
imu2 = mpu9250(mpu_address=0x68) # Sensor titled "CJMCU-1ODOF"
#clock = DS3231(17)
sTime = time.mktime(time.gmtime())

log = open('../logs/dataTemp.log', 'w+')    # Currently set to overwrite the current file. PLEASE change to 'a+' before real testing!
log.write('temp1 refers to the temperature recorded by "CJMCU-MPU". temp2 refers to the temperature recorded by "CJMCU-1ODOF')
log.write('time (s) temp1 (C) temp2 (c)\n')
print('temp1 refers to the temperature recorded by "CJMCU-MPU". temp2 refers to the temperature recorded by "CJMCU-1ODOF')
print('time (s) temp1 (C) temp2 (c)\n')
# Also the 1ODOF sensor is probably damaged... sorry
x = 0

while x == 0:
    try:
        temp = imu.temp
        temp2 = imu2.temp
        nTime = time.mktime(time.gmtime())
        difference = int(nTime) - int(sTime)
        print(f'{difference} {round(temp,5)} {round(temp2,5)}\n')
        log.write(f'{difference} {round(temp,5)} {round(temp2,5)}\n')
        time.sleep(1)
    except KeyboardInterrupt:
        x = 1
