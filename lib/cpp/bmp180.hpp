#ifndef BMP_180
#define BMP_180

//#include "i2c_device.hpp"
#include "sensor.hpp"

constexpr std::string_view BMP180_NAME{"BMP180"};
constexpr int BMP180_I2C{0x77};

constexpr int MEASUREMENT_CONTROL{0xF4};
constexpr int TEMPERATURE_MEASURE{0xEE};
constexpr int PRESSURE_MEASURE{0x74};

constexpr int READ_MEASUREMENT{0xF6}
constexpr int READ_CALIBRATION{0xAA};

// TODO: Include inheritance from I2CDevice and modify constructors
/*
  Example Sensor that tests reading from I2CBus using I2CDevice class
  Reads pressure and temperature from sensor's I2C bus

  * - Inherited from I2CDevice

  Parameters:
    std::string_view s_name* -> name of the sensor
    int s_i2c_address* -> I2C Address that sensor occupies on I2C bus
*/
class BMP180 : public Sensor {

private:
  float m_temperature{};
  float m_pressure{};
  float m_altitude{};

  void CalibrateTemp();
  void CalibratePressure();

public:
  // Constructor parameters will be initialized with I2CDevice constructor
  BMP180(std::string_view s_name=BMP180_NAME, int s_i2c_address=BMP180_I2C);

  // read from sensor -> calibrate -> update calibrated temp -> return it
  float ReadTemp();
  float ReadPressure();
  float ReadAltitude();

  // TODO: Determine alternative return type for read()
  // Read from all functions specified. Return array
  float ReadSensor();
};

#endif
