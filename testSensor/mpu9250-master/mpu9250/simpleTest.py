import datetime as dt
import tmp102
from mpu9250 import mpu9250
mySensor = mpu9250()
l = open("log.csv", "w")
# Initialize communication with TMP102
tmp102.init()
while True:
    print(mySensor.accel)
    print(mySensor.gyro)
    print(mySensor.mag)
    print(mySensor.temp)
    l.write("%s,%s,%s,%s"%mySensor.accel[0],mySensor.accel[1],mySensor.accel[2])
