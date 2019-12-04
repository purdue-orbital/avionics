import sys, os

sys.path.append(os.path.abspath(os.path.join('..','lib')))

from mpu9 import MPU9250
from time import sleep

if __name__ == '__main__':
	print("\t--- Gyro test ---\n")
	imu = MPU9250("test")
	while True:
		x,y,z = imu.gyro
		print(f"Gyro: {x:.3f} {y:.3f} {z:.3f} dps")
		sleep(1)
