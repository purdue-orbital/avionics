#include "sensor.hpp"

Sensor::Sensor(std::string_view name, int i2c_address)
: I2CDevice{i2c_address, name}
{
}

float Sensor::ReadSensor() {
    std::cout << "Base class ReadSensor function" << std::endl;
    return 1.0;
}
