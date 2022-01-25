#pragma once
#include <iostream>

class I2CDevice {
public:
  // don't know type for constructor attributes
  I2CDevice(int address, std::string name);
private:
  long int read();
  std::vector<long int> read_block(int register_);
  void write(int register_, int data);
  
};
