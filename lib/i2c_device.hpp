#pragma once

#include <string>
#include <vector>
#include <fcntl.h>

class I2CDevice {
/*
  parent class for all sensors
*/
public:
  // don't know type for constructor attributes
  I2CDevice(int address, std::string name);
private:
  std::string name;
  int address;
  int bus; //open working i2c bus (using bus 1 in python implementation)

  int open_smbus();
  long int read(int register_);
  std::vector<long int> read_block(int register_, int num);
  long int write(int register_, int data);

};
