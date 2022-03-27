#ifndef MPU_9250
#define MPU_9250

//#include "i2c_device.hpp"
#include "sensor.hpp"

constexpr std::string_view MPU9_NAME{"MPU9"};
constexpr int MPU9_I2C{0x69};

// TODO: Include inheritance from I2CDevice and modify constructors
/*
  Example Sensor that tests reading from I2CBus using I2CDevice class
  Reads gyroscope and acceleration from sensor's I2C bus

  * - Inherited from I2CDevice

  Parameters:
    std::string_view s_name* -> name of the sensor
    int s_i2c_address* -> I2C Address that sensor occupies on I2C bus
*/
class MPU9 : public Sensor {

private:
  float m_acceleration{};
  float m_angular_velocity{};

  // TODO: Container for acceleration and gyroscope components ie array? vector?
  float CalibrateAcceleration();
  float CalibrateAngularVelocity();

public:
  // Constructor parameters will be initialized with I2CDevice constructor
  MPU9(std::string_view s_name=MPU9_NAME, int s_i2c_address=MPU9_I2C);

  // read from sensor -> calibrate -> update calibrated temp -> return it
  float ReadAcceleration();
  float ReadAngularVelocity();

  // TODO: Determine alternative return type for read()
  // Read from all functions specified. Return array
  virtual float ReadSensor();
};


#endif
