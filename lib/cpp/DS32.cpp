#include "DS32.hpp"

DS3231::DS3231(std::string_view s_name, int s_i2c_address):
Sensor{s_name, s_i2c_address}, time{0}{
  wiringPiSetupGpio();
  pinMode(CLOCK_PIN, OUTPUT);

  //Sets 1.024 kHz mode for square wave on SQW pin
  write(CONTROL_REGISTER, 0b01101000);

  if ((read(CONTROL_REGISTER) & 0b01101000) != 0b01101000)
    throw std::invalid_argument("DS3231 mode not set correctly!");

  //Create read thread for INT pin (17)
  wiringPiISR(CLOCK_PIN, INT_EDGE_RISING, &tick);
  //GPIO.add_event_detect(CLOCK_PIN, GPIO.RISING, callback=self.tick)
}

DS3231::~DS3231(){
  //something
}

void* DS3231::tick(auto channel){
  //something
}

int DS3231::GetTime(){
  //something
  return 0;
}

void DS3231::SetTime(float value){
  //something
}

int DS3231::GetTemp(){
  //something
  return 0;
}

void DS3231::SetTemp(float value){
  //something
}

inline void ERROR_HANDLER(int command){
  exit(command);
}

int main(){
  DS3231 clock{"DS3231"};

  try {
    while (true){
      std::cout<< clock.time << std::endl;
      std::cout<< clock.temp << std::endl;
      sleep(1);
    }
  } catch (...){
    printf("Interrupt initiated. Stop!\n");
    signal(SIGINT, ERROR_HANDLER);
  }

  return 0;
}
