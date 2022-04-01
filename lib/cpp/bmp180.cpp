#include "bmp180.hpp"
#include <climits>


void InitializeCalibration() {
  
}

/*
  Read the sensor's temperature from the I2C bus and
  perform operations on data

  returns float of calibrated pressure data
*/
void BMP180::CalibrateTemp() {
  X1 = (temp - AC6) * AC5 / 32768.0;
  X2 = (MC * 2048.0) / (X1 + MD);
  B5 = X1 + X2;

  std::cout << "BMP180 temperature calibrated" << std::endl;
  return B5;
}

/*
  Read the sensor's pressure from the I2C bus and
  perform operations on data to update pressure

*/
void BMP180::CalibratePressure() {
  B6 = B5 - 4000;
  X1 = (B2 * (B6 * B6 / 4096.0)) / 2048.0;
  X2 = AC2 * B6 / 2048.0;
  X3 = X1 + X2;
  B3 = (((AC1 * 4 + X3) * 2) + 2) / 4.0;
  X1 = AC3 * B6 / 8192.0;
  X2 = (B1 * (B6 * B6 / 2048.0)) / 65536.0;
  X3 = ((X1 + X2) + 2) / 4.0;
  B4 = AC4 * (X3 + 32768) / 32768.0;
  B7 = ((pres - B3) * (25000.0));
  if (B7 < LONG_MAX)
    m_pressure = (B7 * 2) / B4;
  else
    m_pressure = (B7 / B4) * 2;
  X1 = (m_pressure / 256.0) * (m_pressure / 256.0);
  X1 = (X1 * 3038.0) / 65536.0;
  X2 = ((-7357) * m_pressure) / 65536.0;
  std::cout << "BMP180 pressure calibrated" << std::endl;
}

/*
  Update and return the temperature

  returns float temperature
*/
float BMP180::ReadTemp() {
  float c_temp_data = CalibrateTemp();
  m_temperature = ((c_temp_data + 8.0) / 16.0) / 10.0;
  std::cout << "Read BMP180 temperature: " << m_temperature << std::endl;

  return m_temperature;
}

/*
  Update and return the pressure

  returns float pressure in hPa
*/
float BMP180::ReadPressure() {
  float c_pressure_data = CalibratePressure();

  std::cout << "Read BMP180 pressure: " << m_pressure << std::endl;

  return m_pressure;
}

/*
  Update and read the altitude using the sensor's pressure and temperature

  returns float altitude
*/
float BMP180::ReadAltitude() {
  // TODO: Replace literals with physical variables
  m_altitude = 44330 * (1 - pow((m_pressure / 1013.25), 0.1903));
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
  BMP180 test{"test"};

  float value = test.ReadSensor();

  return 0;
}
