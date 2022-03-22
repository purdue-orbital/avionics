#include "bmp180.hpp"

void BMP180::calibrateTemp(){
  return;
}

void BMP180::calibratePressure(){
  return;
}

float BMP180::readTemp(){
  // get temperature and return
  return ;
}

float BMP180::readPressure(){
  // get pressure and return
  return ;
}

float BMP180::readAltitude(){
  // get altitude and return

  return ;
}

float BMP180::read(){
  // get altitude and return
  readPressure();
  readTemperature();
  readAltitude();
  return ;
}
