# The MIT License (MIT)
#
# Copyright (c) 2016 Philip R. Moyer and Radomir Dopieralski for Adafruit Industries.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import smbus
import time
import RPi.GPIO as GPIO  
GPIO.setmode(GPIO.BCM)

# Set bus to /dev/12c-1 (rather than -0)
bus = smbus.SMBus(1)

DS32_ADDRESS = 0x68
CONTROL_REGISTER = 0x0e
TEMP_REGISTER = 0x11
SQW = 0

class DS3231:
    """Interface to the DS3231 RTC."""
    
    def __init__(self, pin):

        self.SQW = 0

        # Set GPIO pin to read clock interrupt
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Sets 1.024 kHz mode for square wave on SQW pin
        bus.write_byte_data(DS32_ADDRESS, CONTROL_REGISTER, 0b01101000)
        
        if (bus.read_byte_data(DS32_ADDRESS, CONTROL_REGISTER) & 0b01101000) != 0b01101000:
            raise ValueError("DS3231 mode not set correctly!")
        
        # Create read thread for INT pin (17)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=self.tick)

    def tick(self, channel):
        self.SQW += 1

    @property
    def time(self):
        return self.SQW / 1024.0

    @property
    def temp(self):
        msb = bus.read_byte_data(DS32_ADDRESS, TEMP_REGISTER)
        lsb = bus.read_byte_data(DS32_ADDRESS, TEMP_REGISTER + 1)
        return msb + (lsb >> 6) * 0.25

        
if __name__ == "__main__":    
    clock = DS3231(17)
    
    try:
        while True:
            print("{:.3f}".format(clock.time))
            print("{:.2f}".format(clock.temp))
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stop.\n")
        GPIO.cleanup()
    
