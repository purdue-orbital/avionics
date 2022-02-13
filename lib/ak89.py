from i2c_device import I2CDevice

AK8963_ADDRESS = 0x0C
MAGNET_DATA = 0x03
AK_DEVICE_ID = 0x48
AK_WHO_AM_I = 0x00
AK8963_8HZ = 0x02
AK8963_100HZ = 0x06
AK8963_14BIT = 0x00
AK8963_16BIT = 0x01 << 4
AK8963_CNTL1 = 0x0A
AK8963_CNTL2 = 0x0B
AK8963_ASAX = 0x10
AK8963_ST1 = 0x02


class AK8963(I2CDevice):
    def __init__(self, name, ak_address=AK8963_ADDRESS):
        """
        Setup the Magnetometer

        Needs to be initialized after the MPU9250 s.t. they are on the same network
        """
        super(AK8963, self).__init__(ak_address, name)

        if self.read(AK_WHO_AM_I) is not AK_DEVICE_ID:
            raise Exception("AK8963: init failed to find device")
        self.write(AK8963_CNTL1, (AK8963_16BIT | AK8963_8HZ))

    def read_xyz(self, register):
        """
        Reads x, y, and z axes at once and turns them into a tuple.
        """
        # data is MSB, LSB, MSB, LSB ...
        data = self.read_block(register, 6)

        # data = []
        # for i in range(6):
        #       data.append(self.read8(address, register + i))

        # all 3 are set to 16b or 14b readings, we have take half, so one bit is
        # removed 16 -> 15 or 13 -> 14
        lsb = 4800 / 2 ** 15

        x = self.conv(data[0], data[1]) * lsb
        y = self.conv(data[2], data[3]) * lsb
        z = self.conv(data[4], data[5]) * lsb

        return (x, y, z)

    def conv(self, msb, lsb):
        """
        Performs twos complement of 2-byte number
        """
        value = lsb | (msb << 8)
        if value >= (1 << 15):
            value -= 1 << 16

        return value

    @property
    def mag(self):
        return self.read_xyz(MAGNET_DATA)
