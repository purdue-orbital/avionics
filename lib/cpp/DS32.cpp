#include "DS32.hpp"

DS3231::DS3231(std::string_view name){
  //super(DS3231, self).__init__(DS32_ADDRESS, name)
  time = 0;


  /*
      GPIO.setmode(GPIO.BCM)
      # Set GPIO pin to read clock interrupt
      GPIO.setup(CLOCK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  */

  //Sets 1.024 kHz mode for square wave on SQW pin
  write(CONTROL_REGISTER, 0b01101000);

  if ((read(CONTROL_REGISTER) & 0b01101000) != 0b01101000)
    throw std::invalid_argument("DS3231 mode not set correctly!");

  //Create read thread for INT pin (17)
  //GPIO.add_event_detect(CLOCK_PIN, GPIO.RISING, callback=self.tick)


}



int main(){
  /*
    clock = DS3231("DS3231")

    try:
        while True:
            print("{:.3f}".format(clock.time))
            print("{:.2f}".format(clock.temp))
            sleep(1)

    except KeyboardInterrupt:
        print("Stop.\n")
  */
  
  return 0;
}
