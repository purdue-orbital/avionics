#include <linux/i2c-dev.h>
#include <i2c/smbus.h>
#include "i2c_device.hpp"

long int read(self, register_) {
  // code to be executed
}

long int read_block(self, register_, num) {
  // code to be executed
}

long int write(self, register_, data) {
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