#include "mpu9.hpp"

/*
  Read the sensor's acceleration from the I2C bus and
  perform operations on data

  returns float of calibrated acceleration data
*/
float MPU9::CalibrateAcceleration() {
  std::cout << "Calibrate MPU9250 acceleration" << std::endl;

  return 1.0;
}

/*
  Read the sensor's angular velocity from the I2C bus and
  perform operations on data

  returns float of calibrated angular velocity data
*/
float MPU9::CalibrateAngularVelocity() {
  std::cout << "Calibrate MPU9250 angular velocity" << std::endl;

  return 1.0;
}

/*
  Update and return the acceleration

  returns float acceleration
*/
float MPU9::ReadAcceleration() {
  CalibrateAcceleration();
  std::cout << "Read MPU9250 acceleration" << std::endl;

  return 1.0;
}

/*
  Update and return the angular velocity

  returns float angular velocity
*/
float MPU9::ReadAngularVelocity() {
  // get orientation and return
  CalibrateAngularVelocity();
  std::cout << "Read MPU9250 angular velocity" << std::endl;

  return 1.0;
}

/*
  Update and read the acceleration and angular velocity from the sensor

  returns float array of acceleration and angular velocity
*/
float MPU9::read() {
  ReadAcceleration();
  ReadAngularVelocity();
  return 1.0;
}

/*
  Test MPU9 constructor and read functions
*/
int main() {
  MPU9 test = MPU9(MPU9_NAME, MPU9_I2C);

  float value = test.read();

  return 0;
}
