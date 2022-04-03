#include "bmp180.hpp"
#include <climits>

/*
  Fill the sensor's calibration coefficients at sensor initialization

*/
// TODO: Add a Boolean to express if calibration initialized successfully
void BMP180::InitializeCalibration(int _register) {
  i2c_block_t data = read_block(_register, 22);

  bool check = false;
  AC1 = ToLSBFirst(data[0], data[1], check);
  AC2 = ToLSBFirst(data[2], data[3], check);
  AC3 = ToLSBFirst(data[4], data[5], check);
  AC4 = ToLSBFirst(data[6], data[7], check);
  AC5 = ToLSBFirst(data[8], data[9], check);
  AC6 = ToLSBFirst(data[10], data[11], check);
  B1 = ToLSBFirst(data[12], data[13], check);
  B2 = ToLSBFirst(data[14], data[15], check);
  MB = ToLSBFirst(data[16], data[17], check);
  MC = ToLSBFirst(data[18], data[19], check);
  MD = ToLSBFirst(data[20], data[21], check);
}

/*
  Read the sensor's temperature from the I2C bus and
  perform operations on data

  returns float of calibrated pressure data
*/
long BMP180::CalibrateTemp() {
  write(MEASUREMENT_CONTROL, TEMPERATURE_MEASURE);
  usleep(SLEEP_TEMP_DELAY);

  std::cout << AC1 << std::endl;

  i2c_block_t data = read_block(READ_MEASUREMENT, 2);
  long temp = ToLSBFirst(data[0], data[1]);
  X1 = (temp - AC6) * AC5 / 32768.0;
  X2 = (MC * 2048.0) / (X1 + MD);
  B5 = X1 + X2;

  std::cout << "BMP180 temperature calibrated to " << B5 << std::endl;
  return B5;
}

/*
  Read the sensor's pressure from the I2C bus and
  perform operations on data to update pressure

*/
double BMP180::CalibratePressure(int oss) {
  long double pressure{0.0};
  long wait_time{SLEEP_2MS_DELAY + (SLEEP_3MS_DELAY << oss)};

  write(MEASUREMENT_CONTROL, (PRESSURE_MEASURE + (oss<<6)));

  usleep(wait_time);

  i2c_block_t data = read_block(READ_MEASUREMENT, 3);

  long pres =
            ((data[0] << 16) |
            (data[1] << 8) |
            data[2]) >> (8-oss);

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

  if (B7 < LONG_MAX) {
    pressure = (B7 * 2) / B4;
  } else {
    pressure = (B7 / B4) * 2;
  }
  std::cout << oss << std::endl;

  X1 = (pressure / 256.0) * (pressure / 256.0);
  X1 = (X1 * 3038.0) / 65536.0;
  X2 = ((-7357) * pressure) / 65536.0;
  std::cout << "BMP180 pressure calibrated to " << pressure << std::endl;
  return pressure;
}

/*
  Update and return the temperature

  returns float temperature
*/
double BMP180::ReadTemp() {
  double c_temp_data = CalibrateTemp();
  m_temperature = ((c_temp_data + 8.0) / 16.0) / 10.0;
  std::cout << "Read BMP180 temperature: " << m_temperature << std::endl;

  return m_temperature;
}

/*
  Update and return the pressure

  returns float pressure in hPa
*/
double BMP180::ReadPressure() {
  double c_pressure_data = CalibratePressure();

  m_pressure = c_pressure_data + ((X1 + X2 + 3791) / 16) / 100;
  std::cout << "Read BMP180 pressure: " << m_pressure << std::endl;

  return m_pressure;
}

/*
  Update and read the altitude using the sensor's pressure and temperature

  returns float altitude
*/
double BMP180::ReadAltitude() {
  // TODO: Replace literals with physical variables
  m_altitude = 44330 * (1 - pow((m_pressure / 1013.25), 0.1903));
  std::cout << "Read BMP180 altitude: " << m_altitude << std::endl;

  return m_altitude;
}

/*
  Update and read the pressure, temperature, and altitude from the sensor

  returns float array of pressure, temperature, and altitude
*/
float BMP180::ReadSensor() {
  ReadTemp();
  ReadPressure();
  ReadAltitude();
  return 1.0;
}

BMP180::BMP180(std::string_view s_name, int s_i2c_address)
: Sensor(s_name, s_i2c_address)
{
  InitializeCalibration();
  std::cout << "BMP180 constructed with " << GetName() << " and " << GetAddress() << std::endl;
}

/*
  Test BMP180 constructor and read functions
*/
int main() {
  BMP180 test{"test"};

  double value = test.ReadSensor();

  return 0;
}
