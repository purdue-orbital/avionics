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
  float c_acceleration = CalibrateAcceleration();
  m_acceleration = c_acceleration;
  std::cout << "Read MPU9250 acceleration: " << m_acceleration << std::endl;

  return m_acceleration;
}

/*
  Update and return the angular velocity

  returns float angular velocity
*/
float MPU9::ReadAngularVelocity() {
  float c_angular_velocity = CalibrateAngularVelocity();
  m_angular_velocity = c_angular_velocity;
  std::cout << "Read MPU9250 angular velocity: " << m_angular_velocity << std::endl;

  return 1.0;
}

/*
  Update and read the acceleration and angular velocity from the sensor

  returns float array of acceleration and angular velocity
*/
float MPU9::ReadSensor() {
  ReadAcceleration();
  ReadAngularVelocity();
  return 1.0;
}

MPU9::MPU9(std::string_view s_name, int s_i2c_address)
: Sensor(s_name, s_i2c_address)
{
  std::cout << "MPU9 constructed with " << s_name << " and " << s_i2c_address << std::endl;
}


/*
  Test MPU9 constructor and read functions
*/
int main() {
  MPU9 test{MPU9_NAME, MPU9_I2C};

  float value = test.ReadSensor();

  return 0;
}
