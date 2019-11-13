import json
import shutil
import RPi.GPIO as GPIO

with open('./send/[action notes].json') as f:
    datain = json.load(f)

ROCKET_LONG = datain['rocket'][0]['t_1']
ROCKET_LATI = datain['rocket'][0]['t_2']

ROCKET_ALT = datain['rocket'][0]['alt']

ROCKET_GYRO_X = datain['rocket'][0]['g_x']
ROCKET_GYRO_Y = datain['rocket'][0]['g_y']
ROCKET_GYRO_Z = datain['rocket'][0]['g_z']

ROCKET_MAGNET_X = datain['rocket'][0]['m_x']
ROCKET_MAGNET_Y = datain['rocket'][0]['m_y']
ROCKET_MAGNET_z = datain['rocket'][0]['m_z']

ROCKET_TEMP = datain['rocket'][0]['p']

ROCKET_ACC_X = datain['rocket'][0]['a_x']
ROCKET_ACC_Y = datain['rocket'][0]['a_y']
ROCKET_ACC_Z = datain['rocket'][0]['a_z']


BAL_LONG = datain['balloon'][0]['t_1']
BAL_LATI = datain['balloon'][0]['t_2']

BAL_ALT = datain['balloon'][0]['alt']

BAL_GYRO_X = datain['balloon'][0]['g_x']
BAL_GYRO_Y = datain['balloon'][0]['g_y']
BAL_GYRO_Z = datain['balloon'][0]['g_z']

BAL_MAGNET_X = datain['balloon'][0]['m_x']
BAL_MAGNET_Y = datain['balloon'][0]['m_y']
BAL_MAGNET_z = datain['balloon'][0]['m_z']

BAL_TEMP = datain['balloon'][0]['p']

BAL_ACC_X = datain['balloon'][0]['a_x']
BAL_ACC_Y = datain['balloon'][0]['a_y']
BAL_ACC_Z = datain['balloon'][0]['a_z']

GPIO.setmode(GPIO.BCM)


Outputsignal = pin#

GPIO.setup(Inputsignal,GPIO.IN)
GPIO.setup(Outputsignal,GPIO.OUT)


while GPIO.input(ignition) == True:
        GPSCOND = (ROCKET_LONG == BAL_LONG) and (ROCKET_LAT == BAL_LAT)
        GYROCOND = (ROCKET_GYRO_X == BAL_GYRO_X) and (ROCKET_GYRO_Y == BAL_GYRO_Y) and (ROCKET_GYRO_Z == BAL_GYRO_Z)
        TEMPCOND = (ROCKET_TEMP == BAL_TEMP)
        MAGCOND = (ROCKET_MAG_X == BAL_MAG_X) and (ROCKET_MAG_Y == BAL_MAG_Y) and (ROCKET_MAG_Z == BAL_MAG_Z)
        ACCCOND = (ROCKET_ACC_X == BAL_ACC_X) and (ROCKET_ACC_Y == BAL_ACC_Y) and (ROCKET_ACC_Z == BAL_ACC_Z)
        ALTCOND = (ROCKET_ALT == BAL_ALT)
        condition = GPSCOND and GYROCOND and TEMPCOND and MAGCOND and ACCCOND and ALTCOND
    if (testmode):
        while GPIO.input(condition) == True:
            class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
            time.sleep(3)
            class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(False), pin_factory(None))
    else if (pre-launch):
        while GPIO.input(condition) == True:
            class gpiozero.OutputDevice (Outputsignal, active_high(True) ,initial_value(False), pin_factory(None))
            time.sleep(10)
            class gpiozero.OutputDevice (Outputsignal, active_high(False) ,initial_value(False), pin_factory(None))


shutil.move('./send/[action notes].json','./archive')

##GPIO.cleanup()



