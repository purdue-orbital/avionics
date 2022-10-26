import serial, time

class Heater:
    def __init__(self):
        self.arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
    
    @property
    def status(self):
        last = self.poll()
        return last

    def poll(self):
        if arduino.isOpen():
            while arduino.inWaiting()==0: pass
            if arduino.inWaiting()>0:
                ans = arduino.readline()
                return ans
                arduino.flushInput()
            

if __name__ == '__main__':
    h = Heater()
    print(h.status())
