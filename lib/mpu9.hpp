#ifndef MPU_9250
#define MPU_9250

//#include "i2c_device.hpp"
#include <iostream>

constexpr std::string_view MPU9_NAME{"MPU9"};
constexpr int MPU9_I2C{0x69};

// TODO: Include inheritance from I2CDevice and modify constructors
/*
  Example Sensor that tests reading from I2CBus using I2CDevice class
  Reads gyroscope and acceleration from sensor's I2C bus

  * - Inherited from I2CDevice

  Inputs:
    std::string_view name* -> name of the sensor
    int i2c_address* -> I2C Address that sensor occupies on sensor bus
*/
class MPU9 {

private:
  // Two fields below will be replaced with I2CDevice's versions
  std::string_view name;
  int i2c_address;

  float acceleration;
  float angular_velocity;

  // TODO: Container for acceleration and gyroscope components ie array? vector?
  float CalibrateAcceleration();
  float CalibrateAngularVelocity();

public:
  // Constructor parameters will be initialized with I2CDevice constructor
  MPU9(std::string_view s_name, int s_i2c_address)
  : name(s_name), i2c_address(s_i2c_address)
  {
    std::cout << "MPU9 constructed with " << s_name << " and " << s_i2c_address << std::endl;
  }

  // read from sensor -> calibrate -> update calibrated temp -> return it
  float ReadAcceleration();
  float ReadAngularVelocity();

  // TODO: Determine alternative return type for read()
  // Read from all functions specified. Return array
  float read();
};


#endif
