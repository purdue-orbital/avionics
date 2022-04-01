#include "sensor.hpp"

Sensor::Sensor(std::string_view name, int i2c_address)
: I2CDevice{i2c_address, name}
{
}

int Sensor::ToLSBFirst(int msb, int lsb) {
  int value = (msb << 8) | lsb;
  if (value >> 15)
    return (value - (1 << 16));
  return value;
}

float Sensor::ReadSensor() {
    std::cout << "Base class ReadSensor function" << std::endl;
    return 1.0;
}
