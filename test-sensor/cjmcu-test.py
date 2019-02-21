# this is a test of I2C connection for the Pi
import smbus
import time

address = 0x68
bus = smbus.SMBus(1)

try:
	while True:
		print("output: {}".format(bus.read_byte_data(address, 1)))
		time.sleep(0.2)
except KeyboardInterrupt as error:
	print("\n{}\n".format(error))
