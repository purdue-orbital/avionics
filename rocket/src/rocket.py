import RPi.GPIO as GPIO

from data_aggr import Sensors

balloon_out_pin = 27
balloon_in_pin = 22


if __name__ == "__main__":
    # Set balloon_out_pin to high
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(balloon_out_pin, GPIO.OUT)
    GPIO.output(balloon_out_pin, GPIO.HIGH)

    # Set falling edge detection on balloon_in_pin

    GPIO.setup(balloon_in_pin, GPIO.IN)
    GPIO.wait_for_edge(balloon_in_pin, GPIO.FALLING)

    # Log time of balloon disconnect

    sens = Sensors("Rocket Computer") 
    sens.log.write("balloon disconnect @ ")

    # Start data logging

    print("Running data_aggr.py ...\n")
    
    while True:
        sens.read_all()
        sens.printd()
