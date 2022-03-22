#ifndef SENSOR_PROCESS
#define SENSOR_PROCESS

#include "i2c_device.hpp"

class SensorProcess {

private:
  std::vector<I2CDevice> polling_list;
  int polling_rate;
public:

}

#endif
