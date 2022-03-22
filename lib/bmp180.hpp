#ifndef BMP_180
#define BMP_180

#include "i2c_device.hpp"

constexpr std::string BMP180_NAME{"BMP180"};
constexpr int BMP180_I2C{0x77};

class BMP180 : public I2CDevice {

private:
  float* temperature{};
  float* pressure{};

  // currently unknown return type; change later
  void calibrateTemp();
  void calibratePressure();

public:
  // read from sensor -> calibrate -> update calibrated temp -> return it

  BMP180() : I2CDevice(BMP180_NAME, BMP180_I2C)
  {
  }

  float readTemp();
  float readPressure();
  float readAltitude();

  // Read from all functions specified. Return array
  float read();
};

#endif
