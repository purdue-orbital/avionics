from data_aggr import Sensors
from time import sleep

if __name__ == '__main__':
    print("Running data_aggr.py ...\n")

    sens = Sensors("MPU9250")

    while True:
        a = sens.readAccel()
        g = sens.readGyro()
        m = sens.readMagnet()
        t = sens.readTemperature()
        
        print("Accel: {:.3f} {:.3f} {:.3f} g".format(*a))
        print("Gyro: {:.3f} {:.3f} {:.3f} dps".format(*g))
        print("Magnet: {:.3f} {:.3f} {:.3f} mT".format(*m))
        print(f"Temp: {t} C")
        
        sleep(1)

        
