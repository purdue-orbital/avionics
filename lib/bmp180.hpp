#ifndef BMP_180
#define BMP_180

#include "i2c_device.hpp"

class BMP180: public I2CDevice {

private:
  // currently unknown return type; change later
  //
  float temperature;
  float pressure;

  void calibrateTemp();
  void calibratePressure();
  void pollTemp(); // read from sensor -> calibrate -> update calibrated temp
  void pollPressure();

public:



  float readTemp();
  float readPressure();
  float readAltitude();
};

#endif
