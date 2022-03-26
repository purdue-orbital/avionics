#ifndef SENSOR_ABSTRACT
#define SENSOR_ABSTRACT

// #include "i2c_device.hpp"
#include <iostream>

// TODO: Include inheritance from I2CDevice and modify constructors
/*
  Abstract Sensor Class for general sensor functions and fields

  * - Inherited from I2CDevice

  Parameters:
    std::string_view name* -> name of the sensor
    int i2c_address* -> I2C Address that sensor occupies on sensor bus
*/
class Sensor {

protected:
  std::string_view m_name;
  int m_i2c_address;

public:
  Sensor(std::string_view name, int i2c_address);

  virtual float ReadSensor();
};

#endif
