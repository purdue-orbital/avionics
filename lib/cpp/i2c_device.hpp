#ifndef I2C_DEVICE_H
#define I2C_DEVICE_H

#include <string>
#include <vector>
#include <cmath>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <iostream>

extern "C" {
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <i2c/smbus.h>
}

using i2c_t = long;
using i2c_block_t = std::vector<i2c_t>;

class I2CDevice {
/*
  parent class for all sensors
*/
protected:
  //__s32 read(__u8 register_);
  //std::vector<__s32> read_block(__u8 register_, int num);
  //__s32 write(__u8 register_, __u8 data);
public:
  // don't know type for constructor attributes
  I2CDevice(int i2c_address, std::string_view device_name);

  i2c_t read(uint8_t register_);
  i2c_block_t read_block(uint8_t register_, int num);
  i2c_t write(uint8_t register_, uint8_t data);

  std::string_view GetName();
  int GetAddress();

private:
  std::string_view m_name{};
  int m_address{};
  int m_bus{}; //open working i2c bus (using bus 1 in python implementation)

  int open_smbus();
};

#endif
