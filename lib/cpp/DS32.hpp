#ifndef DS32
#define DS32

#include "sensor.hpp"
#include <wiringPi.h> // CPP EQUIVALENT TO RPi.GPIO
#include <unistd.h>
#include "signal.h" // USED TO CATCH KEYBOARD INTERRUPTS

static constexpr int DS32_ADDRESS{0x68};
static constexpr int CONTROL_REGISTER{0x0e};
static constexpr int TEMP_REGISTER{0x11};
static constexpr int CLOCK_PIN{17};

class DS3231 : public Sensor{
public:
  DS3231(std::string_view s_name, int s_i2c_address);

  void tick(auto channel);
  int GetTime();
  void SetTime(float value);
  float GetTemp();
  void SetTemp(float value);

  ~DS3231();
private:
  int time;
};

#endif
