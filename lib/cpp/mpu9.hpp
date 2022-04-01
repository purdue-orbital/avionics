#ifndef MPU_9250
#define MPU_9250

#include "sensor.hpp"

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
  static constexpr std::string_view MPU9_NAME{"MPU9"};
  static constexpr int MPU9250_ADDRESS{0x69};
  static constexpr int DEVICE_ID{0x71};
  static constexpr int WHO_AM_I{0x75};
  static constexpr int PWR_MGMT_1{0x6B};
  static constexpr int INT_PIN_CFG{0x37};
  static constexpr int INT_ENABLE{0x38};

  static constexpr int ACCEL_DATA{0x3B};
  static constexpr int ACCEL_CONFIG{0x1C};
  static constexpr int ACCEL_CONFIG2{0x1D};
  static constexpr int ACCEL_2G{0x00};
  static constexpr int ACCEL_4G{(0x01 << 3)};
  static constexpr int ACCEL_8G{(0x02 << 3)};
  static constexpr int ACCEL_16G{(0x03 << 3)};

  static constexpr int TEMP_DATA{0x41};

  static constexpr int GYRO_DATA{0x43};
  static constexpr int GYRO_CONFIG{0x1B};
  static constexpr int GYRO_250DPS{0x00};
  static constexpr int GYRO_500DPS{((0x01 << 3))};
  static constexpr int GYRO_1000DPS{((0x02 << 3))};
  static constexpr int GYRO_2000DPS{((0x03 << 3))};

  static constexpr double alsb{2.0 / ~(1<<16)};
  static constexpr double glsb{250.0 / ~(1<<16)};

  double m_acceleration{};
  double m_angular_velocity{};

  // TODO: Container for acceleration and gyroscope components ie array? vector?
  int ToLSBFirst(int msb, int lsb);
  double ReadXYZ(double _register, double lsb);

public:
  // Constructor parameters will be initialized with I2CDevice constructor
  MPU9(std::string_view s_name=MPU9_NAME, int s_i2c_address=MPU9250_ADDRESS);

  // read from sensor -> calibrate -> update calibrated temp -> return it
  float ReadAcceleration();
  float ReadAngularVelocity();

  // TODO: Determine alternative return type for read()
  // Read from all functions specified. Return array
  virtual float ReadSensor();
};


#endif
