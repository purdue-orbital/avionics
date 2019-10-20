from ds3231 import DS3231
import board
import busio
import time

if __name__ == '__main__':
    i2c = busio.I2C(board.SCL, board.SDA)
    clock = DS3231(i2c)

    while True:
        t= clock.datetime
        #print(f'{clock.datetime()}')
        print("{}:{:02}:{:02}\n".format(t.tm_hour, t.tm_min, t.tm_sec))
        time.sleep(1)
        
