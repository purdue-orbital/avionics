#include "i2c_device.hpp"

I2CDevice::I2CDevice(int address_, std::string name_)
{
  name = name_;
  address = address_;
  bus = open_smbus();
  // bus = smbus(1); // open i2c bus 1
}

// TODO: currently causing a linker error
int
I2CDevice::open_smbus()
{
  int file;
  char* filename = "/dev/i2c-1";
  if ((file = open(filename, O_RDWR)) < 0) {
    /* ERROR HANDLING: you can check errno to see what went wrong */
    perror("Failed to open the i2c bus");
    exit(1);
  }

  return file;
}

__s32
I2CDevice::read(__u8 register_)
{
  // initiate communication with peripheral sensor
  if (ioctl(bus, I2C_SLAVE, address) < 0) {
    /* ERROR HANDLING; you can check errno to see what went wrong */
    exit(1);
  }

  // read 1 byte from register
  return i2c_smbus_read_word_data(address, register_);
}

std::vector<__s32>
I2CDevice::read_block(__u8 register_, int num)
{
  // data to read
  std::vector<__s32> data;

  for (int i = 0; i < num; i++)
    data.push_back(read(register_ + i));

  return data;
}

__s32
I2CDevice::write(__u8 register_, __u8 data)
{
  return i2c_smbus_write_byte_data(address, register_, data);
}

int main() {
  I2CDevice test_sensor = I2CDevice(SENSOR_ADDRESS, "BMP180");

	std::vector<__s32> data = test_sensor.read_block(0xAA, 22);

	__s32 AC1;
	__s32 AC2;
	__s32 AC3;
	__s32 AC4;
	__s32 AC5;
	__s32 AC6;
	__s32 B1;
	__s32 B2;
	__s32 MB;
	__s32 MC;
	__s32 MD;
	float B3;
	float B4;
	float B5;
	float B6;
	float B7;
	float X1;
	float X2;
	float X3;
	__s32 pres;

	AC1 = data[0] * 256 + data[1];
	if (AC1 > 32767) {
		AC1 -= 65535;
	}
	AC2 = data[2] * 256 + data[3];
	if (AC2 > 32767) {
		AC2 -= 65535;
	}
	AC3 = data[4] * 256 + data[5];
	if (AC3 > 32767) {
		AC3 -= 65535;
	}
	AC4 = data[6] * 256 + data[7];
	AC5 = data[8] * 256 + data[9];
	AC6 = data[10] * 256 + data[11];
	B1 = data[12] * 256 + data[13];
	if (B1 > 32767) {
		B1 -= 65535;
	}
	B2 = data[14] * 256 + data[15];
	if (B2 > 32767) {
		B2 -= 65535;
	}
	MB = data[16] * 256 + data[17];
	if (MB > 32767) {
		MB -= 65535;
	}
	MC = data[18] * 256 + data[19];
	if (MC > 32767) {
		MC -= 65535;
	}
	MD = data[20] * 256 + data[21];
	if (MD > 32767) {
		MD -= 65535;
	}

	sleep(0.5);

	// Select measurement control register, 0xF4
	// Measure temperature 0xE2
	test_sensor.write(0xF4, 0xE2);

	sleep(0.5);

	data = test_sensor.read_block(0xF6, 2);
	__s32 temp = data[0] * 256 + data[1];

	// Select measurement control register, 0xF4
	// Measure pressure 0x74
	test_sensor.write(0xF4, 0x74);
	sleep(0.5);

	data = test_sensor.read_block(0xF6, 2);

	pres = ((data[0] * 65536) + (data[1] * 256) + data[2]) / 128;

	X1 = (temp - AC6) * AC5 / 32768.0;
	X2 = (MC * 2048.0) / (X1 + MD);
	B5 = X1 + X2;
	float cTemp = ((B5 + 8.0) / 16.0) / 10.0;
	float fTemp = cTemp * 1.8 + 32;

	B6 = B5 - 4000;
	X1 = (B2 * (B6 * B6 / 4096.0)) / 2048.0;
	X2 = AC2 * B6 / 2048.0;
	X3 = X1 + X2;
	B3 = (((AC1 * 4 + X3) * 2) + 2) / 4.0;
	X1 = AC3 * B6 / 8192.0;
	X2 = (B1 * (B6 * B6 / 2048.0)) / 65536.0;
	X3 = ((X1 + X2) + 2) / 4.0;
	B4 = AC4 * (X3 + 32768) / 32768.0;
	B7 = ((pres - B3) * (25000.0));
	float pressure = 0.0;

	if (B7 < 2147483648L) {
		pressure = (B7 * 2) / B4;
	}
	else {
		pressure = (B7 / B4) * 2;
	}
	X1 = (pressure / 256.0) * (pressure / 256.0);
	X1 = (X1 * 3038.0) / 65536.0;
	X2 = ((-7357) * pressure) / 65536.0;
	pressure = (pressure + (X1 + X2 + 3791) / 16.0) / 100;

	// Calculate Altitude
	float altitude = 44330 * (1 - pow((pressure / 1013.25), 0.1903));


	printf("Altitude : %.2f\n", altitude);
	printf("Pressure : %.2f\n", pressure);
	printf("Temperature in Celsius : %.2f\n", cTemp);
	printf("Temperature in Fahrenheit : %.2f\n", fTemp);

  return 0;
}

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
