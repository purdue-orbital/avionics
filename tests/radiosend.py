import sys, os

sys.path.append(os.path.abspath(os.path.join('..', 'lib')))
sys.path.append(os.path.abspath(os.path.join('..', 'src')))
#from Radio import Radio
from RadioBeta import Radio
from control import Control
from datetime import datetime, timedelta
import json
import _thread as thread
import time

gsradio = Radio(1,True)

def run():
    print("Running control.py ...\n")

    with Control("balloon") as ctrl:
        mode = 2 # mode 1 = testmode / mode 2 = pre-launch mode

            # Data collection needs to be running parallel to rest of program
        collect = ctrl.Collection(lambda: ctrl.read_data(self.proxy), 1)
        collect.start()

    while True:
        # Control loop to determine radio disconnection
        result = ctrl.connection_check()
        endT = datetime.now() + timedelta(seconds=10)  # Wait 5 min. to reestablish signal
        while ((result == None) & (datetime.now() < endT)):
                result = ctrl.connection_check()
                sleep(0.5)  # Don't overload CPU

                # These don't need to be parallel to the radio connection, since we won't
                # be getting commands if the radio is down
        if result == 0:
            ctrl.qdm_check(0)
        else:
                # Receive commands and iterate through them
            if ctrl.getLaunchFlag():
                ctrl.ignition(mode)
            if ctrl.getQDMFlag():
                ctrl.qdm_check(0)
            if ctrl.getAbortFlag():
                ctrl.abort()
            if ctrl.getStabFlag:
                ctrl.stabalize()
                sleep(1)
#            ctrl.qdm_check(0)
#            sleep(3)
#            ctrl.ignition(2)
thread.start_new_thread(run, ())

endT = datetime.now() + timedelta(seconds=300)  # Wait 5 min. to reestablish signal
while ((datetime.now() < endT)):
    jsonData = {}
    jsonData['QDM'] = True
    jsonData['LAUNCH'] = True
    jsonData['ABORT'] = True
    jsonData['STAB'] = True
    gsradio.send(json.dumps(jsonData))
    time.sleep(0.5)
