from data_aggr_old import SerialPort
from time import sleep

if __name__ == "__main__":
    sensors = SerialPort("Arduino", "/dev/ttyUSB0")

    try:
        while True:
            sensors.writeDict()
    except KeyboardInterrupt:
        print('\nEnding experiment...\n')
