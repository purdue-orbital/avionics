import RPi.GPIO as GPIO
from time import sleep

from sensors import Sensors

BALLOON_OUT_PIN = 27
BALLOON_IN_PIN = 22


if __name__ == "__main__":
    # Set balloon_out_pin to high
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BALLOON_OUT_PIN, GPIO.OUT)
    GPIO.output(BALLOON_OUT_PIN, GPIO.HIGH)

    # Set falling edge detection on balloon_in_pin

    # GPIO.setup(BALLOON_IN_PIN, GPIO.IN)
    # GPIO.wait_for_edge(BALLOON_IN_PIN, GPIO.FALLING)

    # Log time of balloon disconnect
    # sens.log.write("balloon disconnect @ {:.2f}\n".format(sens.clock.time))

    # Start data logging
    with Sensors("balloon") as sensors:
        # Lambda used to pass generic multi-arg functions to sensors.add
        # These will later be executed in unique threads
        sensors.add(lambda: sensors.temperature(write=True), 1, identity="temp",
            token="temp (C)", access=lambda: sensors.temperature()
        )

        sensors.add(lambda: sensors.accel(write=True), 1, identity="acc",
            token="ax (g),ay (g),az (g)", access=lambda: sensors.accel()
        )

        sensors.add(lambda: sensors.gyro(write=True), 1, identity="gyro",
            token="gx (dps),gy (dps),gz (dps)", access=lambda: sensors.gyro()
        )

        sensors.add(lambda: sensors.gps(write=True), 1, identity='gps',
            token="lat,long,alt (m)", access=lambda: sensors.gps()
        )

        sensors.add(lambda: sensors.print(), 1)

        ### DON'T CHANGE ###
        sensors.add(lambda: sensors.time(), sensors.greatest, token="time (s)")
        sensors.write_header()
        sensors.add(lambda: sensors.write(), sensors.greatest)
        sensors.stitch()
        ### DON'T CHANGE ###
        
        while True:
            sleep(1)
