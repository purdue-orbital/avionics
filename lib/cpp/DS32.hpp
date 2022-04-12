#ifndef DS32
#define DS32

#include "i2c_device.hpp"
#include <wiringPi.h> // CPP EQUIVALENT TO RPi.GPIO
#include <time.h>

static constexpr int DS32_ADDRESS{0x68};
static constexpr int CONTROL_REGISTER{0x0e};
static constexpr int TEMP_REGISTER{0x11};
static constexpr int CLOCK_PIN{17};

class DS3231 : public I2CDevice{
public:
  DS3231(std::string_view name);

  void tick(auto channel);
  int GetTime();
  void SetTime(float value);
  float GetTemp();
  void SetTemp(float value);
  
  ~DS3231();
private:
  int time{0};
}

#endif
