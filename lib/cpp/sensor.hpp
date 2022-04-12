#ifndef SENSOR_ABSTRACT
#define SENSOR_ABSTRACT

#include "i2c_device.hpp"

// TODO: Include inheritance from I2CDevice and modify constructors
/*
  Abstract Sensor Class for general sensor functions and fields

  * - Inherited from I2CDevice

  Parameters:
    std::string_view name* -> name of the sensor
    int i2c_address* -> I2C Address that sensor occupies on sensor bus
*/
class Sensor : public I2CDevice {
protected:
    template <typename T>
    T ToLSBFirst(T msb, T lsb, bool check=false) {
      T value = (msb << 8) | lsb;
      if (check && (value >> 15))
        return (value - (1 << 16));
      return value;
    }
public:
  Sensor(std::string_view name, int i2c_address);

  virtual float ReadSensor();
};

#endif
