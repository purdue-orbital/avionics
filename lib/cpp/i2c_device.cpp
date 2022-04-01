#include "i2c_device.hpp"

std::string_view I2CDevice::GetName() {
    return m_name;
}

int I2CDevice::GetAddress() {
  return m_address;
}

I2CDevice::I2CDevice(int i2c_address, std::string_view device_name)
: m_address{i2c_address}, m_name{device_name}, m_bus{open_smbus()}
{
  //m_bus = open_smbus();
  // bus = smbus(1); // open i2c bus 1
}

// TODO: currently causing a linker error
int I2CDevice::open_smbus()
{
  int file;
  char filename[20];
  snprintf(filename, 19, "/dev/i2c-1");
  file = open(filename, O_RDWR);
  if (file < 0) {
    /* ERROR HANDLING: you can check errno to see what went wrong */
    perror("Failed to open the i2c bus");
    exit(1);
  }
  return file;
}

i2c_t I2CDevice::read(uint8_t register_)
{
  // initiate communication with peripheral sensor
  if (ioctl(m_bus, I2C_SLAVE, m_address) < 0) {
    /* ERROR HANDLING; you can check errno to see what went wrong */
    exit(1);
  }

  // read 1 byte from register
    return i2c_smbus_read_byte_data(m_bus, register_);
}

i2c_block_t I2CDevice::read_block(uint8_t register_, int num)
{
  // data to read
  i2c_block_t data;

  for (int i = 0; i < num; i++)
    data.push_back(read(register_ + i));

  return data;
}

i2c_t I2CDevice::write(uint8_t register_, uint8_t data) {
  if (ioctl(m_bus, I2C_SLAVE, m_address) < 0) {
    /* ERROR HANDLING; you can check errno to see what went wrong */
    exit(1);
  }
  return i2c_smbus_write_byte_data(m_bus, register_, data);
}

int conv(int msb, int lsb) {
  int value = (msb << 8) | lsb;
  if (value >> 15)
    return (value - (1 << 16));
  return value;
}

void test_bmp180() {
  // Create I2C bus
  I2CDevice test(0x77, "BMP180");

  // Choose oversampling setting
  constexpr int oss{1};

	// Calibration Cofficients stored in EEPROM of the device
	// Read 22 bytes of data from address 0xAA(170)
	i2c_block_t data = test.read_block(0xAA, 22);

	// Convert the data
	short AC1 = data[0] << 8 | data[1];
  printf("%d\n", AC1);
	short AC2 = data[2] << 8 | data[3];
	short AC3 = data[4] << 8 | data[5];
	unsigned short AC4 = data[6] << 8 | data[7];
	unsigned short AC5 = data[8] << 8 | data[9];
	unsigned short AC6 = data[10] << 8 | data[11];
	short B1 = data[12] << 8 | data[13];
	short B2 = data[14] << 8 | data[15];
	short MB = data[16] << 8 | data[17];
	short MC = data[18] << 8 | data[19];
	short MD = data[20] << 8 | data[21];

	sleep(0.5);

	// Select measurement control register(0xF4)
	// Enable temperature measurement(0x2E)
	test.write(0xF4, 0x2E);

	sleep(4.5/1000.0);

	// Read 2 bytes of data from register(0xF6)
	// temp msb, temp lsb
  data = test.read_block(0xF6, 2);

	// Convert the data
  // temp <-> uncompensated temperature
	long temp = data[0] << 8 | data[1];

	// Select measurement control register(0xf4)
	// Enable pressure measurement, OSS = 1(0x74)
	test.write(0xF4, (0x34 + (oss<<6)));
	sleep(0.2);

	// Read 3 bytes of data from register(0xF6)
	// pres msb1, pres msb, pres lsb
	data = test.read_block(0xF6, 3);

	// Convert the data
  // pres <-> uncompensated pressure
	long pres =
                ((data[0] << 16) |
                (data[1] << 8) |
                data[2]) >> (8-oss);

	// Callibration for Temperature
	long X1 = (temp - AC6) * AC5 >> 15;
	long X2 = (MC << 11) / (X1 + MD);
	long B5 = X1 + X2;
	double cTemp = ((B5 + 8) >> 4) / 10.0;
	double fTemp = cTemp * 1.8 + 32;

	// Calibration for Pressure
	long B6 = B5 - 4000;
	X1 = (B2 * (B6 * B6 >> 12)) >> 11;
	X2 = (AC2 * B6) >> 11;
	long X3 = X1 + X2;
  // LOOK AT THIS v v
	long B3 = (((AC1 * 4 + X3) << oss) + 2) >> 2;

  X1 = (AC3 * B6) >> 13;
	X2 = (B1 * (B6 * B6 >> 12)) >> 16;
	X3 = ((X1 + X2) + 2) >> 2;
	unsigned long B4 = AC4 * (unsigned long)(X3 + 32768) >> 15;
  // Oversampling Setting: 1
	unsigned long B7 = ((unsigned long)pres - B3) * (50000 >> oss);

	long double pressure = 0.0;
	if(B7 < 2147483648L)
	{
		pressure = (B7 << 1) / B4;
	}
	else
	{
		pressure = (B7 / B4) << 1;
	}
	X1 = (pressure / 256) * (pressure / 256);
	X1 = (X1 * 3038) >> 16;
	X2 = ((-7357) * pressure) / 65536;

	pressure += ((X1 + X2 + 3791) / 16) / 100;

	// Calculate Altitude
	double altitude = 44330 * (1 - pow(pressure / 1013.25, 0.1903));

	// Output data to screen
	printf("Altitude : %.2f m \n", altitude);
	printf("Pressure : %.2f hPa \n", pressure);
	printf("Temperature in Celsius : %.2f C \n", cTemp);
	printf("Temperature in Fahrenheit : %.2f F \n", fTemp);
}

void test_mpu9() {
  // Create I2C bus
  I2CDevice test(0x69, "MPU9250");

  //std::cout << test.read(0x75) << std::endl;
  if(test.read(0x75) != 0x71)
    std::cout << "Failed to find device" << std::endl;

  test.write(0x6B, 0x00);
  sleep(0.2);
  test.write(0x6B, 0x01);
  test.write(0x1C, 0x00);
  test.write(0x1B, 0x00);

  test.write(0x37, 0x22);
  test.write(0x38, 0x01);
  sleep(0.1);

  double alsb = 2.0 / ~(1<<16);
  double glsb = 250.0 / ~(1<<16);

  double a_x{};
  double a_y{};
  double a_z{};
  double g_x{};
  double g_y{};
  double g_z{};
  double temp_out{};
  double temp{};

  while(true) {
  sleep(0.2);
  i2c_block_t accel_data = test.read_block(0x3B, 6);
  a_x = conv(accel_data[0], accel_data[1]) * alsb;
  a_y = conv(accel_data[2], accel_data[3]) * alsb;
  a_z = conv(accel_data[4], accel_data[5]) * alsb;

  i2c_block_t gyro_data = test.read_block(0x43, 6);
  g_x = conv(gyro_data[0], gyro_data[1]) * glsb;
  g_y = conv(gyro_data[2], gyro_data[3]) * glsb;
  g_z = conv(gyro_data[4], gyro_data[5]) * glsb;

  i2c_block_t temp_data = test.read_block(0x41, 2);
  temp_out = temp_data[0] << 8 | temp_data[1];
  temp = temp_out / 333.87 + 21.0;

  printf("Acceleration : % 06.4f %.4f %.4f g\n", a_x, a_y, a_z);
	printf("Gyroscope    : % 06.4f %.4f %.4f dps\n", g_x, g_y, g_z);
  printf("Temperature  : % 06.2f C\n", temp);
  }
}

/*
int main() {
  test_mpu9();
  //test_bmp180();

}
*/
/*    PYTHON CODE THAT NEEDS TO BE CONVERTED TO C++ ABOVE:
      def __init__(self, address, name):
        self.address = address
        self.name = name

        # Set bus to /dev/i2c-1
        self.bus = smbus.SMBus(1)

      def read(self, register):
        return self.bus.read_byte_data(self.address, register)

      def read_block(self, register, num):
        data = []
        for i in range(0, num):
          data.append(self.read(register + i))

        return data

      def write(self, register, data):
        self.bus.write_byte_data(self.address, register, data)
*/
