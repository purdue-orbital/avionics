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
  CalibrateTemp();
  std::cout << "Read BMP180 temperature" << std::endl << std::endl;

  return 1.0;
}

/*
  Update and return the pressure

  returns float return
*/
float BMP180::ReadPressure() {
  CalibratePressure();
  std::cout << "Read BMP180 pressure" << std::endl << std::endl;

  return 1.0;
}

/*
  Update and read the altitude using the sensor's pressure and temperature

  returns float altitude
*/
float BMP180::ReadAltitude() {
  std::cout << "Read BMP180 altitude" << std::endl << std::endl;

  return 1.0;
}

/*
  Update and read the pressure, temperature, and altitude from the sensor

  returns float array of pressure, temperature, and altitude
*/
float BMP180::read() {
  ReadPressure();
  ReadTemp();
  ReadAltitude();
  return 1.0;
}

//BMP180::BMP180(std::string_view s_name, int s_i2c_address) {
//}

/*
  Test BMP180 constructor and read functions
*/
int main() {
  BMP180 test = BMP180(BMP180_NAME, BMP180_I2C);

  float value = test.read();

  return 0;
}
