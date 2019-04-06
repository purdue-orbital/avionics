import smbus
import time

bus = smbus.SMBus(1)

print(bus.write_byte_data(0x77,0x2E,0XEE))
