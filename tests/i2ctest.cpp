#ifndef WIN_32
#include <Windows.h>
#else
#include <unistd.h>
#endif

#include <stdio.h>
#include <math.h>

#include "../lib/i2c_device.hpp"

// BMP180 Address: 0x77
#define SENSOR_ADDRESS 0x77

int main() {
	I2CDevice test_sensor = I2CDevice(SENSOR_ADDRESS, "BMP180");
	
	std::vector<__s32> data = test_sensor.read_block(0xAA, 22);
	
	__s32 AC1;
	__s32 AC2;
	__s32 AC3;
	__s32 AC4;
	__s32 AC5;
	__s32 AC6;
	__s32 B1;
	__s32 B2;
	__s32 MB;
	__s32 MC;
	__s32 MD;
	float B3;
	float B4;
	float B5;
	float B6;
	float B7;
	float X1;
	float X2;
	
	AC1 = data[0] * 256 + data[1];
	if (AC1 > 32767) 
		AC1 -= 65535;
	AC2 = data[2] * 256 + data[3];
	if (AC2 > 32767)
		AC2 -= 65535;
	AC3 = data[4] * 256 + data[5];
	if (AC3 > 32767)
		AC3 -= 65535;
	AC4 = data[6] * 256 + data[7];
	AC5 = data[8] * 256 + data[9];
	AC6 = data[10] * 256 + data[11];
	B1 = data[12] * 256 + data[13];
	if (B1 > 32767)
		B1 -= 65535;
	B2 = data[14] * 256 + data[15];
	if (B2 > 32767)
		B2 -= 65535;
	MB = data[16] * 256 + data[17];
	if (MB > 32767)
		MB -= 65535;
	MC = data[18] * 256 + data[19];
	if (MC > 32767)
		MC -= 65535;
	MD = data[20] * 256 + data[21];
	if (MD > 32767)
		MD -= 65535;
	
	sleep(0.5);
	
	// Select measurement control register, 0xF4
	// Measure temperature 0xE2
	test_sensor.write(0xF4, 0xE2);
	
	sleep(0.5);
	
	data = test_sensor.read_block(0xF6, 2);
	__s32 temp = data[0] * 256 + data[1];

	// Select measurement control register, 0xF4
	// Measure pressure 0xE2	
	test_sensor.write(0xF4, 0x74);
	sleep(0.5);

	data = test_sensor.read_block(0xF6, 2);
	
	X1 = (temp - AC6) * AC5 / 32768.0;
	X2 = (MC * 2048.0) / (X1 + MD);
	B5 = X1 + X2;
	float cTemp = ((B5 + 8.0) / 16.0) / 10.0;
	float fTemp = cTemp * 1.8 + 32;
	
	B6 = B5 - 4000;
	X1 = (B2 * (B6 * B6 / 4096.0)) / 2048.0;
	X2 = AC2 * B6 / 2048.0;
	X3 = X1 + X2;
	B3 = (((AC1 * 4 + X3) * 2) + 2) / 4.0
	X1 = AC3 * B6 / 8192.0;
	X2 = (B1 * (B6 * B6 / 2048.0)) / 65536.0;
	X3 = ((X1 + X2) + 2) / 4.0;
	B4 = AC4 * (X3 + 32768) / 32768.0;
	B7 = ((pres - B3) * (25000.0));
	float pressure = 0.0;

	if (B7 < 2147483648L) {
		pressure = (B7 * 2) / B4;
	}
	else {
		pressure = (B7 / B4) * 2;
	}
	X1 = (pressure / 256.0) * (pressure / 256.0);
	X1 = (X1 * 3038.0) / 65536.0;
	X2 = ((-7357) * pressure) / 65536.0;
	pressure = (pressure + (X1 + X2 + 3791) / 16.0) / 100;

	// Calculate Altitude
	float altitude = 44330 * (1 - pow((pressure / 1013.25), 0.1903));

	
	printf("Altitude : %.2f\n", );
	printf("Pressure : %.2f\n", );
	printf("Temperature in Celsius : %.2f\n", );
	printf("Temperature in Fahrenheit : %.2f\n", );
	
	return 0;
} 