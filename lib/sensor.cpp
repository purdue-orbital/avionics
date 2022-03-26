#include "sensor.hpp"

Sensor::Sensor(std::string_view name, int i2c_address)
: m_name(name), m_i2c_address(i2c_address)
{
}

float Sensor::ReadSensor() {
    std::cout << "Base class ReadSensor function" << std::endl;
    return 1.0;
}
