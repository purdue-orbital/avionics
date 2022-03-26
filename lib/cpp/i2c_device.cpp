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
