// #include <linux/i2c-dev.h>
// #include <i2c/smbus.h>
#include "i2c_device.hpp"

I2CDevice::I2CDevice(int address_, std::string name_) {
  name = name_;
  address = address_;
  bus = open_smbus();
  //bus = smbus(1); // open i2c bus 1
}

// TODO: currently causing a linker error 
int I2CDevice::open_smbus(){
  int file;
  char* filename = "/dev/i2c-1";
  if ((file = open(filename, O_RDWR)) < 0) {
    /* ERROR HANDLING: you can check errno to see what went wrong */
    perror("Failed to open the i2c bus");
    exit(1);
  }

  return file;
}

long int I2CDevice::read(int register_) {
  // code to be executed
}

std::vector<long int> I2CDevice::read_block(int register_, int num) {
  // code to be executed
  std::vector<long int> data;

  for (int i=0; i<num; i++)
    data.push_back(read(register_+i));

  return data;
}

long int I2CDevice::write(int register_, int data) {
  // code to be executed
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
