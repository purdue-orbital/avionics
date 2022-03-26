#ifndef SENSOR_PROCESS
#define SENSOR_PROCESS

#include "i2c_device.hpp"

class SensorProcess {

private:
  std::vector<I2CDevice> polling_list{};
  int polling_rate{};
  FILE* log{};

public:
  SensorProcess(int poll_frequency, FILE* log_file)
  : polling_rate(poll_frequency), log(log_file)
  {
  }

  void add(I2CDevice sensor);
}

#endif
