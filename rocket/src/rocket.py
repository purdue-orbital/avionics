import RPi.GPIO as GPIO

from data_aggr import Sensors

balloon_out_pin = 27
balloon_in_pin = 22

def balloon_disconnect(log):
    """
    Callback function when balloon_out_pin falls

    Writes launch time to log file
    """
    ### TODO: Finish writing launch time + recieving time from ds32 ###
    log.write()

if __name__ == "__main__":
    # Set balloon_out_pin to high
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(balloon_out_pin, GPIO.OUT)
    GPIO.output(balloon_out_pin, GPIO.HIGH)

    # Set rising edge detection on balloon_in_pin

    GPIO.setup(balloon_in_pin, GPIO.IN)
    GPIO.add_event_detect(balloon_in_pin, GPIO.RISING, callback=ballon_disconnect(sens.log))

    # Start data logging
    print("Running data_aggr.py ...\n")
    
    sens = Sensors("Rocket Computer")

    while True:
        sens.read_all()
        sens.printd()
