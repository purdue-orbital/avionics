import gpsd
from time import sleep

class NEO7M():
    def __init__(self):
        gpsd.connect()

    @property
    def position(self):
        last = self.poll()
        
        return last.position(), last.altitude()    
        
    def poll(self):
        return gpsd.get_current()
        

if __name__ == "__main__":

    gps = NEO7M();

    while True:
        try:
            print(gps.position)
        except UserWarning as e:
            print(e)

        sleep(1)
