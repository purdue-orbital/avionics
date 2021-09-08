import time
import random
import sys
import RPi.GPIO as GPIO

QDM_PIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(QDM_PIN, GPIO.OUT)

def QDM(userInput):
    if userInput == 1:
        print("QDM active\n")
        GPIO.output(QDM_PIN, GPIO.LOW)
        sys.exit("Program ended\n")
        GPIO.cleanup()
    else:
        print("QDM inactive\n")
        GPIO.output(QDM_PIN, GPIO.HIGH)


def main(connection):
    #if we have a stable connection, pass in the command into the qdm function
    if connection:
        userInput = int(input("QDM command:")) #where radio input will come from
        QDM(userInput)
        time.sleep(3)
    else:
        print("connection unstable...wait 30 seconds \n")
        time.sleep(5)
        connection = round(random.randint(0, 1)) #get status of connection
        #detach if connection is still not active
        if connection == 0:
            QDM(1)






#runs constantly and passes through the connection status
def getConnection():
    #code to get the connection from ground station
    while True:
        connection = 1
        main(connection)



getConnection()

