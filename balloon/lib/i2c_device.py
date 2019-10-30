import smbus

class I2CDevice:
    """
    Parent class for all sensors
    """

    def __init__(self, address, name):
        self.address = address
        self.name = name

        # Set bus to /dev/i2c-1
        self.bus = smbus.SMBus(1)

    def read(self, register):
        return self.bus.read_byte_data(self.address, register)

    def write(self, register, data):
        self.bus.write_byte_data(self.address, register, data)

    def __del__(self):
        # Any special requirements to close sensor
        self.bus.close()
