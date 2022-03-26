#include "bmp180.hpp"

/*
  Read the sensor's temperature from the I2C bus and
  perform operations on data

  returns float of calibrated pressure data
*/
float BMP180::CalibrateTemp() {
  std::cout << "BMP180 temperature calibrated" << std::endl;

  return 1.0;
}

/*
  Read the sensor's pressure from the I2C bus and
  perform operations on data

  returns float of calibrated pressure data
*/
float BMP180::CalibratePressure() {
  std::cout << "BMP180 pressure calibrated" << std::endl;

  return 1.0;
}

/*
  Update and return the temperature

  returns float temperature
*/
float BMP180::ReadTemp() {
  float c_temp_data = CalibrateTemp();
  m_temperature = c_temp_data;
  std::cout << "Read BMP180 temperature: " << m_temperature << std::endl;

  return m_temperature;
}

/*
  Update and return the pressure

  returns float pressure
*/
float BMP180::ReadPressure() {
  float c_pressure_data = CalibratePressure();
  m_pressure = c_pressure_data;
  std::cout << "Read BMP180 pressure: " << m_pressure << std::endl;

  return m_pressure;
}

/*
  Update and read the altitude using the sensor's pressure and temperature

  returns float altitude
*/
float BMP180::ReadAltitude() {
  m_altitude = m_pressure + m_temperature;
  std::cout << "Read BMP180 altitude: " << m_altitude << std::endl;

  return 1.0;
}

/*
  Update and read the pressure, temperature, and altitude from the sensor

  returns float array of pressure, temperature, and altitude
*/
float BMP180::ReadSensor() {
  ReadPressure();
  ReadTemp();
  ReadAltitude();
  return 1.0;
}

BMP180::BMP180(std::string_view s_name, int s_i2c_address)
: Sensor(s_name, s_i2c_address)
{
  std::cout << "BMP180 constructed with " << m_name << " and " << m_i2c_address << std::endl;
}

/*
  Test BMP180 constructor and read functions
*/
int main() {
  BMP180 test{BMP180_NAME, BMP180_I2C};

  float value = test.ReadSensor();

  return 0;
}
