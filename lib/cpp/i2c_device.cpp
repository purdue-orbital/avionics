#include "i2c_device.hpp"

std::string_view I2CDevice::GetName() {
    return m_name;
}

int I2CDevice::GetAddress() {
  return m_address;
}

I2CDevice::I2CDevice(int i2c_address, std::string_view device_name)
: m_address{i2c_address}, m_name{device_name}, m_bus{open_smbus()}
{
  //m_bus = open_smbus();
  // bus = smbus(1); // open i2c bus 1
}

// TODO: currently causing a linker error
int I2CDevice::open_smbus()
{
  int file;
  char filename[20];
  snprintf(filename, 19, "/dev/i2c-1");
  file = open(filename, O_RDWR);
  if (file < 0) {
    /* ERROR HANDLING: you can check errno to see what went wrong */
    perror("Failed to open the i2c bus");
    exit(1);
  }
  return file;
}

i2c_t I2CDevice::read(uint8_t register_)
{
  // initiate communication with peripheral sensor
  if (ioctl(m_bus, I2C_SLAVE, m_address) < 0) {
    /* ERROR HANDLING; you can check errno to see what went wrong */
    exit(1);
  }

  // read 1 byte from register
    return i2c_smbus_read_byte_data(m_bus, register_);
}

i2c_block_t I2CDevice::read_block(uint8_t register_, int num)
{
  // data to read
  i2c_block_t data;

  for (int i = 0; i < num; i++)
    data.push_back(read(register_ + i));

  return data;
}

i2c_t I2CDevice::write(uint8_t register_, uint8_t data) {
  if (ioctl(m_bus, I2C_SLAVE, m_address) < 0) {
    /* ERROR HANDLING; you can check errno to see what went wrong */
    exit(1);
  }
  return i2c_smbus_write_byte_data(m_bus, register_, data);
}
