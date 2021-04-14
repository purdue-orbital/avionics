import threading as th
import time
import RPi.GPIO as GPIO
start_time = time.time()
keep_going = True
QDM_PIN = 13
GPIO.setmode(GPIO.BCM)  
GPIO.setup(QDM_PIN, GPIO.OUT)
GPIO.output(QDM_PIN, GPIO.LOW)
def key_capture_thread():
    while True:
        global keep_going
        global start_time
        input()
        if keep_going:
            keep_going = False
            start_time = time.time()
        else:
            keep_going = True
            start_time = time.time()

def run():
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    try:
        while True:
            while keep_going:
                GPIO.output(QDM_PIN,GPIO.HIGH)
                elapsed = time.time() - start_time
                print("GPIO HIGH: %.1f seconds" % (elapsed))
                time.sleep(0.1)
            GPIO.output(QDM_PIN,GPIO.LOW)
            elapsed = time.time() - start_time
            print("GPIO LOW: %.1f seconds" % (elapsed))
            time.sleep(0.1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Killed Succesfully: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA!!!!!!!!!!")

run()
