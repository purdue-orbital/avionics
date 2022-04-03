#ifndef BMP_180
#define BMP_180

//#include "i2c_device.hpp"
#include "sensor.hpp"

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
  static constexpr std::string_view BMP180_NAME{"BMP180"};
  static constexpr int BMP180_I2C{0x77};

  static constexpr int MEASUREMENT_CONTROL{0xF4};
  static constexpr int TEMPERATURE_MEASURE{0x2E};
  static constexpr int PRESSURE_MEASURE{0x34};

  static constexpr int READ_MEASUREMENT{0xF6};
  static constexpr int READ_CALIBRATION{0xAA};

  static constexpr int SLEEP_2MS_DELAY{2000};
  static constexpr int SLEEP_3MS_DELAY{3000};
  static constexpr int SLEEP_TEMP_DELAY{4500};

  short AC1{};
  short AC2{};
  short AC3{};
  unsigned short AC4{};
  unsigned short AC5{};
  unsigned short AC6{};
  short B1{};
  short B2{};
  short MB{};
  short MC{};
  short MD{};

  long X1{};
  long X2{};
  long X3{};
  long B3{};
  unsigned long B4{};
  long B5{};
  long B6{};
  unsigned long B7{};

  double m_temperature{};
  double m_pressure{};
  double m_altitude{};

  long CalibrateTemp();
  double CalibratePressure(int oss=0);

  void InitializeCalibration(int _register=READ_CALIBRATION);

public:
  // Constructor parameters will be initialized with I2CDevice constructor
  BMP180(std::string_view s_name=BMP180_NAME, int s_i2c_address=BMP180_I2C);

  // read from sensor -> calibrate -> update calibrated temp -> return it
  double ReadTemp();
  double ReadPressure();
  double ReadAltitude();

  // TODO: Determine alternative return type for read()
  // Read from all functions specified. Return array
  float ReadSensor();
};

#endif
