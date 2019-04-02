#include "MPU9250.h"
#include <Wire.h>
#include <MS5611.h>


// an MPU9250 object with the MPU_9250 on I2C bus 0 with address 0x69
MPU9250 IMU(Wire, 0x69);

// an MS5611 object for pressure data
MS5611 ms5611;

// stores status of communication with MPU9250
int mpuStatus;
// store status of communication with MS5611
int msStatus;

void setup() {
  
  // initialize Serial at baud rate 115200
  Serial.begin(115200);
  
  // wait until serial is ready
  while(!Serial) {}

  // begin communication with MPU9250
  mpuStatus = IMU.begin();
  if (mpuStatus < 0) {
    // error messages if MPU9250 sensor cannot be connected
    // Message must be prefixed with "ERROR:" for PI to separate error messages from data
    Serial.println("ERROR: MPU9250 initialization unsuccessful");
    Serial.print("ERROR: Status ");
    Serial.println(mpuStatus);
  }

  // begin communication with MS5611
  msStatus = ms5611.begin();
  if (!msStatus) {
    Serial.println("ERROR: MS5611 initialization unsuccessful");
    Serial.print("ERROR: Status");
    Serial.println(msStatus);
  }
}


void loop() {
  // read in new sensor data
  IMU.readSensor();
  long realPressure = ms5611.readPressure();
  
  // display the data in CSV Format
  Serial.print(realPressure);
  Serial.print(",  ");
  
  Serial.print("GPSLNG");
  Serial.print(",  ");
  Serial.print("GPSLAT");
  Serial.print(",  ");
  
  Serial.print(IMU.getGyroX_rads(),6);
  Serial.print(", ");
  Serial.print(IMU.getGyroY_rads(),6);
  Serial.print(", ");
  Serial.print(IMU.getGyroZ_rads(),6);
  Serial.print(", ");

  Serial.print(IMU.getMagX_uT(),6);
  Serial.print(", ");
  Serial.print(IMU.getMagY_uT(),6);
  Serial.print(", ");
  Serial.print(IMU.getMagZ_uT(),6);
  Serial.print(", ");

  Serial.print(IMU.getTemperature_C(),6);
  Serial.print(", ");
  
  Serial.print(IMU.getAccelX_mss(),6);
  Serial.print(", ");
  Serial.print(IMU.getAccelY_mss(),6);
  Serial.print(", ");
  Serial.print(IMU.getAccelZ_mss(),6);

  Serial.println();
  
  delay(200);
}
