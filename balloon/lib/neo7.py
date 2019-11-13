import gpsd
from time import sleep

class NEO7M():
    def __init__(self):
        gpsd.connect()

    def position(self):
        return poll.position()
        
    @property
    def poll(self):
        return gpsd.get_current()
        

if __name__ == "__main__":

    gps = NEO7M();

    while True:
        try:
            print(gps.poll().position())
        except UserWarning as e:
            print(e)

        sleep(1)
