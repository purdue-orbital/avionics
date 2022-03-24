#ifndef BMP_180
#define BMP_180

//#include "i2c_device.hpp"
#include <iostream>

constexpr std::string_view BMP180_NAME{"BMP180"};
constexpr int BMP180_I2C{0x77};

// TODO: Include inheritance from I2CDevice and modify constructors
/*
  Example Sensor that tests reading from I2CBus using I2CDevice class
  Reads pressure and temperature from sensor's I2C bus

  * - Inherited from I2CDevice

  Inputs:
    std::string_view name* -> name of the sensor
    int i2c_address* -> I2C Address that sensor occupies on sensor bus
*/
class BMP180 {

private:
  // Two fields below will be replaced with I2CDevice's versions
  std::string_view name{};
  int i2c_address{};

  float temperature{};
  float pressure{};

  float CalibrateTemp();
  float CalibratePressure();

public:
  // Constructor parameters will be initialized with I2CDevice constructor
  BMP180(std::string_view s_name, int s_i2c_address)
  : name(s_name), i2c_address(s_i2c_address)
  {
    std::cout << "BMP180 constructed with " << s_name << " and " << s_i2c_address << std::endl;
  }

  // read from sensor -> calibrate -> update calibrated temp -> return it
  float ReadTemp();
  float ReadPressure();
  float ReadAltitude();

  // TODO: Determine alternative return type for read()
  // Read from all functions specified. Return array
  float read();
};

#endif
