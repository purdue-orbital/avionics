import serial
import pynmea2

class NEO7M(serial.Serial):
    def __init__(self, port, delay):
        super().__init__(self, port, 9600, timeout=delay)

        self.gps = (0, 'N', 0, 'E', 0)

    def __del__(self):
        self.close()

    def read(self, printing=False):
        found = False
        while (self.inWaiting() > 0) or not found:
            string = self.readline().decode('utf-8')
            
            if (string.find('GGA') > 0):
                found = True
                msg = pynmea2.parse(string)

                if printing:
                    print(
                        "Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s" % (
                            msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units
                        )
                    )

                if msg.lat != '':
                    self.gps = (msg.lat, msg.lat_dir, msg.lon, msg.lon_dir, msg.altitude)
                else:   # Data not valid equates to zeros -- sensor error, but not lethal
                    self.gps = (0, 'ERR', 0, 'ERR', 0)
        
        return self.gps