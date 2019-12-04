from time import sleep
from i2c_device import I2CDevice

################################
# MPU9250
################################
MPU9250_ADDRESS = 0x69
DEVICE_ID       = 0x71
WHO_AM_I        = 0x75
PWR_MGMT_1      = 0x6B
INT_PIN_CFG     = 0x37
INT_ENABLE      = 0x38
# --- Accel ------------------
ACCEL_DATA    = 0x3B
ACCEL_CONFIG  = 0x1C
ACCEL_CONFIG2 = 0x1D
ACCEL_2G      = 0x00
ACCEL_4G      = (0x01 << 3)
ACCEL_8G      = (0x02 << 3)
ACCEL_16G     = (0x03 << 3)
# --- Temp --------------------
TEMP_DATA = 0x41
# --- Gyro --------------------
GYRO_DATA    = 0x43
GYRO_CONFIG  = 0x1B
GYRO_250DPS  = 0x00
GYRO_500DPS  = (0x01 << 3)
GYRO_1000DPS = (0x02 << 3)
GYRO_2000DPS = (0x03 << 3)

        
class MPU9250(I2CDevice):
    def __init__(self, name, mpu_address=MPU9250_ADDRESS):
        """
        Setup the IMU

        reg 0x25: SAMPLE_RATE= Internal_Sample_Rate / (1 + SMPLRT_DIV)
        reg 0x29: [2:0] A_DLPFCFG Accelerometer low pass filter setting
                ACCEL_FCHOICE 1
                A_DLPF_CFG 4
                gives BW of 20 Hz
        reg 0x35: FIFO disabled default - not sure i want this ... just give me current reading

        might include an interface where you can change these with a dictionary:
                setup = {
                        ACCEL_CONFIG: ACCEL_4G,
                        GYRO_CONFIG: AK8963_14BIT | AK8963_100HZ
                }
        """
        super(MPU9250, self).__init__(mpu_address, "MPU9250")

        # let's double check we have the correct device address
        if self.read(WHO_AM_I) is not DEVICE_ID:
            raise Exception('MPU9250: init failed to find device')

        self.write(PWR_MGMT_1, 0x00)  # turn sleep mode off
        sleep(0.2)
        self.write(PWR_MGMT_1, 0x01)  # auto select clock source
        self.write(ACCEL_CONFIG, ACCEL_2G)
        self.write(GYRO_CONFIG, GYRO_250DPS)

        # You have to enable the other chips to join the I2C network
        # then you should see 0x68 and 0x0c from:
        # sudo i2cdetect -y 1
        self.write(INT_PIN_CFG, 0x22)
        self.write(INT_ENABLE, 0x01)
        sleep(0.1)

        # all 3 are set to 16b or 14b readings, we have take half, so one bit is
        # removed 16 -> 15 or 13 -> 14
        self.alsb = 2 / ~(1<<16)	#Previously was 2**15, which would ignore the first
        self.glsb = 250 / ~(1<<16)	#14 bits instead of just ignoring the 16th bit

    def read16(self, register):
        data = self.read_block(register, 2)
        return self.conv(data[0], data[1])

    def read_xyz(self, register, lsb):
        """
        Reads x, y, and z axes at once and turns them into a tuple.
        """
        # data is MSB, LSB, MSB, LSB ...
        data = self.read_block(register, 6)

        # data = []
        # for i in range(6):
        #       data.append(self.read8(address, register + i))

		
        x = self.conv(data[0], data[1]) * lsb	#lsb denotes the accuracy in degrees
        y = self.conv(data[2], data[3]) * lsb	#in this case, lsb is 250 / ~(1<<16) (was 2**15)
        z = self.conv(data[4], data[5]) * lsb	#or 250dps accuracy stored in 15 bits

        # print('>> data', data)
        # ans = self.convv.unpack(*data)
        # ans = struct.unpack('<hhh', data)[0]
        # print('func', x, y, z)
        # print('struct', ans)

        return (x, y, z)

    def conv(self, msb, lsb):
        value = (msb << 8) | lsb
        if (value>>15):
            return (value - (1<<16))
        return value

    @property
    def accel(self):
        return self.read_xyz(ACCEL_DATA, self.alsb)

    @property
    def gyro(self):
        return self.read_xyz(GYRO_DATA, self.glsb)

    @property
    def temp(self):
        """
        Returns chip temperature in C

        pg 33 datasheet:
        Temp_degC = ((Temp_out - Temp_room)/Temp_Sensitivity) + 21 degC
        """
        temp_out = self.read16(TEMP_DATA)
        temp = temp_out / 333.87 + 21.0  # these are from the datasheets
        return temp
