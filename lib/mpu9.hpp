#ifndef MPU_9250
#define MPU_9250

#include "i2c_device.hpp"

class MPU9: public I2CDevice{
private:
  // TODO: Use an array or an alternative
  float acceleration; // This will have three values in it
  float orientation; // Gyroscope data, again with three values

  void calibrateAcceleration();
  void calibrateGyroscope();

public:
  float readAcceleration();
  float readGyroscope();
  
}


#endif
