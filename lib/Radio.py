import zmq
import pmt
import _thread as thread
import os
import json
import logging

OK = "\u001b[32m"
WARN = "\u001b[33m"
ERR = "\u001b[31m"
NORM = "\u001b[0m"


class Radio:
    """ Radio API for transmission and reception

    Allows sending and receiving of data, as well as state tracking through memory and persistent storage.

    TODO: Rework into singleton to maintain class timing across threads for backup QDM system. https://stackoverflow.com/questions/21974029/python-sharing-class-instance-among-threads
    """

    def __init__(self, DEBUG=0):
        """ 
        Initializes states based on existance of persistent file. DEBUG modes are 0 for flight, 1 for radio testing, and 2 for internal testing.
        During the first instantiation of this class in launch the caller must guarentee state.json does not exist or a state conflict may occur
        when in DEBUG 0. Additionally, when in DEBUG 0 or 1, confirm GNU Radio python file is in working directory.
        """
        try:
            if DEBUG < 0 or DEBUG > 2:
                raise TypeError("DEBUG must be 0, 1, or 2")
            
            self.launch = False
            self.qdm = False
            self.abort = False

            if DEBUG == 0:
                if os.path.exists("state.json"):
                    with open('state.json', 'r', encoding='utf-8') as stateFile:
                        state = json.loads(stateFile.read())

                        self.launch = state['LAUNCH']
                        self.qdm = state['QDM']
                        self.abort = state['ABORT']

                        stateFile.close()
                
                else:
                    self.saveState()    

            logging.basicConfig(level=(logging.INFO, logging.DEBUG)[DEBUG > 0], filename='mission.log', format='%(asctime)s %(levelname)s:%(message)s')

            self.queue = None

            self.context = zmq.Context()

            def receive():
                recv_sock = self.context.socket(zmq.PULL)
                
                recv_sock.bind("tcp://127.0.0.1:5001")

                while True:
                    try:
                        message = pmt.to_python(pmt.deserialize_str(recv_sock.recv()))
                        logging.info("Received: " + str(message))

                        jsonData = json.loads(message)

                        if self.launch != jsonData['Launch'] or self.qdm != jsonData['QDM'] or self.abort != jsonData['Abort']:
                            log.warning("State mismatch, resending state")
                            self.sendState()

                        if self.queue is not None:
                            self.queue.append(message)
                        else:
                            print("Queue unbound")
                            logging.error("Queue unbound")    
                    except Exception as e:
                        print("Invalid message received")
                        logging.error(e)

            thread.start_new_thread(receive, ())

            self.sock = self.context.socket(zmq.PUSH)

            if DEBUG == 2:
                self.sock.connect("tcp://127.0.0.1:5001")
            else:
                self.sock.bind("tcp://127.0.0.1:5000")

        except Exception as e:
            print(e)
            logging.error(e)

    def send(self, data, isGroundStation=False):
        """
        Sends JSON formatted data to the socket attached to radio interface.
        For single variable values, do not exceed one layer of depth.
        For multi-variable values, do not exceed two layers of depth.

        Ground Station must append state.
        """
        logging.info(data)
        try:
            jsonData = json.loads(data)

            # Oneway communication, Ground Station controls state.
            if isGroundStation:
                try:
                    self.launch = jsonData['Launch']
                    self.qdm = jsonData['QDM']
                    self.abort = jsonData['Abort']
                else:
                    print("Ground Station did not append state attributes to data")
                    logging.error("Ground Station did not append state attributes to data")

                self.saveState()
            else:
                jsonData['LAUNCH'] = self.launch
                jsonData['QDM'] = self.qdm
                jsonData['ABORT'] = self.abort

        except Exception as e:
            print(e)
            logging.error(e)
            return 0

        try:
            logging.info("Sent: " + data)
            self.sock.send(pmt.serialize_str(pmt.to_pmt(data)))
            print("Sent");
            return 1
        except KeyboardInterrupt:
            print ("interrupt received. shutting down.")
            self.sock.close()
            context.term()
            exit()
        except Exception as e:
            print(e)
            logging.error(e)
            return 0

    def sendState(self):
        state = {}
        state['LAUNCH'] = self.launch
        state['QDM'] = self.qdm
        state['ABORT'] = self.abort

        try:
            logging.info(state)
            message = str.encode(state)
            self.sock.send(pmt.serialize_str(pmt.to_pmt(message)))
            logging.debug("State sent")
            return 1

        except KeyboardInterrupt:
            print ("interrupt received. shutting down.")
            self.sock.close()
            context.term()
            exit()
        except Exception as e:
            print(e)
            logging.error(e)
            return 0

    def getLaunchFlag(self):
        return self.launch

    def getQDMFlag(self):
        return self.qdm

    def getAbortFlag(self):
        return self.abort


    def bindQueue(self, queue):
        """
        Supply a queue reference for data placement. See recvTest.py for example usage.
        """
        self.queue = queue

    def saveState(self):
        state = {}
        state['LAUNCH'] = self.launch
        state['QDM'] = self.qdm
        state['ABORT'] = self.abort

        with open('state.json', 'w+', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=4)

    def close(self):
        try:
            self.sock.close()
        except Exception as e:
            print(e)
            logging.error(e)
