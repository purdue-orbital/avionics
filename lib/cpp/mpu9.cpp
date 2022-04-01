#include "mpu9.hpp"
#include <unistd.h>

/*
  Switch from MSB first to LSB first

  returns LSB-first int
*/
int MPU9::ToLSBFirst(int msb, int lsb) {
  int value = (msb << 8) | lsb;
  if (value >> 15)
    return (value - (1 << 16));
  return value;
}

/*
  Read the sensor's angular velocity from the I2C bus and
  perform operations on data

  returns float of calibrated angular velocity data
*/
double MPU9::ReadXYZ(double _register, double lsb) {
  i2c_block_t data = read_block(_register, 6);

  double x = ToLSBFirst(data[0], data[1]) * lsb;
  double y = ToLSBFirst(data[2], data[3]) * lsb;
  double z = ToLSBFirst(data[4], data[5]) * lsb;

  printf("x: % 06.4f y: % 06.4f z: % 06.4f\n", x, y, z);

  return 1.0;
}

/*
  Update and return the acceleration

  returns float acceleration
*/
float MPU9::ReadAcceleration() {
  m_acceleration = ReadXYZ(ACCEL_DATA, alsb);
  //std::cout << "Read MPU9250 acceleration: " << m_acceleration << std::endl;

  return m_acceleration;
}

/*
  Update and return the angular velocity

  returns float angular velocity
*/
float MPU9::ReadAngularVelocity() {
  m_angular_velocity = ReadXYZ(MPU9::GYRO_DATA, glsb);
  //std::cout << "Read MPU9250 angular velocity: " << m_angular_velocity << std::endl;

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
: Sensor{s_name, s_i2c_address}
{
  std::cout << "MPU9 constructed with " << GetName() << " and " << GetAddress() << std::endl;

  if (read(MPU9::WHO_AM_I) != MPU9::DEVICE_ID) {
    perror("MPU9250: init failed to find device");
    exit(1);
  }

  write(MPU9::PWR_MGMT_1, 0x01);
  sleep(0.2);
  write(MPU9::PWR_MGMT_1, 0x00);
  write(MPU9::ACCEL_CONFIG, ACCEL_2G);
  write(MPU9::GYRO_CONFIG, GYRO_250DPS);

  write(MPU9::INT_PIN_CFG, 0x22);
  write(MPU9::INT_ENABLE, 0x01);
  sleep(0.1);
}


/*
  Test MPU9 constructor and read functions
*/
int main() {
  MPU9 test{"test"};

  float value = test.ReadSensor();

  return 0;
}
