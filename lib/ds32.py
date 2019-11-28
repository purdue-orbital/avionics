from i2c_device import I2CDevice
import RPi.GPIO as GPIO
from time import sleep

### ADDRESSES ###
DS32_ADDRESS = 0x68
CONTROL_REGISTER = 0x0e
TEMP_REGISTER = 0x11

class DS3231(I2CDevice):
    """
    Interface to the DS3231 RTC.
    """
    
    def __init__(self, name, pin):
        super(DS3231, self).__init__(DS32_ADDRESS, name)
        self.time = 0
        self.pin = pin

        GPIO.setmode(GPIO.BCM)
        # Set GPIO pin to read clock interrupt
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Sets 1.024 kHz mode for square wave on SQW pin
        self.write(CONTROL_REGISTER, 0b01101000)
        
        if (self.read(CONTROL_REGISTER) & 0b01101000) != 0b01101000:
            raise ValueError("DS3231 mode not set correctly!")
        
        # Create read thread for INT pin (17)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.tick)

        
    def tick(self, channel):
        self._time += 1

    @property
    def time(self):
        return (self._time / 1024.0)

    @time.setter
    def time(self, value):
        self._time = int(value * 1024)

    @property
    def temp(self):
        msb = self.read(TEMP_REGISTER)
        lsb = self.read(TEMP_REGISTER + 1)
        self.temp = msb + (lsb >> 6) * 0.25
        return (self._temp, )

    @temp.setter
    def temp(self, value):
        self._temp = value

    def __del__(self):
        GPIO.cleanup(self.pin)

        
if __name__ == "__main__":    
    clock = DS3231("DS3231", 17)
    
    try:
        while True:
            print("{:.3f}".format(clock.time))
            print("{:.2f}".format(clock.temp))
            sleep(1)
            
    except KeyboardInterrupt:
        print("Stop.\n")
    
