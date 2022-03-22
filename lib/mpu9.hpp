#ifndef MPU_9250
#define MPU_9250

#include "i2c_device.hpp"

constexpr std::string MPU9_NAME{"MPU9"};
constexpr int MPU9_I2C{0x69};

class MPU9 : public I2CDevice{
private:
  // TODO: Container for acceleration and gyroscope components
  // i.e. array? vector?
  float* acceleration{};
  float* orientation{}

  void calibrateAcceleration();
  void calibrateGyroscope();

public:
  MPU9() : I2CDevice(MPU9_NAME, MPU9_I2C)
  {
  }

  float readAcceleration();
  float readGyroscope();

  // Read from all functions specified. Return array
  float read();
}


#endif
