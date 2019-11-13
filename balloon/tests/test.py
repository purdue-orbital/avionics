from data_aggr import Sensors

if __name__ == '__main__':
    print("Running data_aggr.py ...\n")

    sens = Sensors("MPU9250")

    while True:
        print("Accel: {:.3f} {:.3f} {:.3f} mg".format(sens.readAccel()))
        
        print("Gyro: {:.3f} {:.3f} {:.3f} dps".format(sens.readGyro()))

        print("Magnet: {:.3f} {:.3f} {:.3f} mT".format(sens.readMagnet()))

        
