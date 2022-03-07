#pragma once

#include <string>
#include <vector>
#include <fcntl.h>
#include <sys/ioctl.h>

extern "C" {
#include <linux/i2c-dev.h>
#include <i2c/smbus.h>
}

class I2CDevice {
/*
  parent class for all sensors
*/
public:
  // don't know type for constructor attributes
  I2CDevice(int address, std::string name);
  __s32 read(__u8 register_);
  std::vector<__s32> read_block(__u8 register_, int num);
  __s32 write(__u8 register_, __u8 data);

private:
  std::string name;
  int address;
  int bus; //open working i2c bus (using bus 1 in python implementation)

  int open_smbus();
 // __s32 read(__u8 register_);
 // std::vector<__s32> read_block(__u8 register_, int num);
 // __s32 write(__u8 register_, __u8 data);

};
