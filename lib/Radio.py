import zmq
# import pmt
import _thread as thread
import os
import json
import logging
import socket
import time

OK = "\u001b[32m"
WARN = "\u001b[33m"
ERR = "\u001b[31m"
NORM = "\u001b[0m"

"""
IMPORTANT VERSION NOTE: Due to trouble importing pmt on flight computer, as well as radio inoperability at the current time,
this version does not include the library and as such will not work with GNU Radio.

This can be resolved in the future by uncommenting the lines referencing pmt and commenting out the extraneous send commands.
"""

class Radio:
    """ Radio API for transmission and reception

    Allows sending and receiving of data, as well as state tracking through memory and persistent storage.

    TODO: Rework into singleton to maintain class timing across threads for backup QDM system. https://stackoverflow.com/questions/21974029/python-sharing-class-instance-among-threads
    """

    def __init__(self, DEBUG=0, isGroundStation = False, hostname = '127.0.0.1'):
        """ 
        Initializes states based on existance of persistent file. DEBUG modes are 0 for flight, 1 for radio testing, and 2 for ethernet testing, 3 for internal testing.
        During the first instantiation of this class in launch the caller must guarentee state.json does not exist or a state conflict may occur
        when in DEBUG 0. Additionally, when in DEBUG 0 or 1, confirm GNU Radio python file is in working directory.
        """
        try:
            if DEBUG < 0 or DEBUG > 3:
                raise TypeError("DEBUG must be 0, 1, 2, or 3")
            if DEBUG != 2 and hostname != '127.0.0.1':
                raise TypeError("hostname should not be changed unless in DEBUG mode 2")
            
            self.launch = False
            self.qdm = False
            self.abort = False
            self.stab = False

            self.DEBUG = DEBUG
            self.isGroundStation = isGroundStation
            self.hostname = (hostname)

            if self.DEBUG == 0:
                if os.path.exists("state.json"):
                    with open('state.json', 'r', encoding='utf-8') as stateFile:
                        state = json.loads(stateFile.read())

                        self.launch = state['LAUNCH']
                        self.qdm = state['QDM']
                        self.abort = state['ABORT']
                        self.stab = state['STAB']

                        stateFile.close()
                
                else:
                    self.saveState()    

            logging.basicConfig(level=(logging.INFO, logging.DEBUG)[self.DEBUG > 0], filename='mission.log', format='%(asctime)s %(levelname)s:%(message)s')

            self.queue = None

            # Set reception up
            if DEBUG == 1:
                def receive(recv_socket):
                    while True:
                        try:
                            # message is transmitted as binary and needs to be decoded
                            message = recv_sock.recv().decode("utf-8")
                            # message = pmt.to_python(pmt.deserialize_str(recv_sock.recv()))
                            logging.info("Received: " + str(message))

                            jsonData = json.loads(message)

                            if self.launch != jsonData['LAUNCH'] or self.qdm != jsonData['QDM'] or self.abort != jsonData['ABORT'] or self.stab != jsonData['STAB']:
                                logging.warning("State mismatch, resending state")
                                self.sendState()

                            if self.queue is not None:
                                self.queue.append(message)
                            else:
                                print("Queue unbound")
                                logging.error("Queue unbound")    
                        except Exception as e:
                            print("Invalid message received")
                            logging.error(e)

                context = zmq.Context()  

                recv_sock = context.socket(zmq.PULL)
                recv_sock.bind("tcp://127.0.0.1:5001")

                thread.start_new_thread(receive, (recv_sock))

                self.sock = context.socket(zmq.PUSH)

            elif self.DEBUG == 2 or self.DEBUG == 3:
                def receive():
                    if self.isGroundStation:
                        self.socket.listen(300) #Listen for 5 minutes
                        (clientsocket, address) = self.socket.accept()
                        self.socket = clientsocket

                    while True:
                        try:
                            message = self.socket.recv(2048).decode("ascii")
                            logging.info("Received: " + str(message))

                            jsonData = json.loads(message)

                            if self.launch != jsonData['LAUNCH'] or self.qdm != jsonData['QDM'] or self.abort != jsonData['ABORT'] or self.stab != jsonData['STAB']:
                                logging.warning("State mismatch, resending state")
                                self.sendState()

                            if self.queue is not None:
                                self.queue.append(message)
                            else:
                                print("Queue unbound")
                                logging.error("Queue unbound")    
                        except Exception as e:
                            print("Invalid message received")
                            logging.error(e)

                if self.isGroundStation:
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.bind((('127.0.0.1', socket.gethostname()) [self.DEBUG == 2], 5000))
                else:
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.connect((self.hostname, 5000))

                thread.start_new_thread(receive, ())

        except Exception as e:
            print(e)
            logging.error(e)


    def send(self, data):
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
            if self.isGroundStation:
                try:
                    self.launch = jsonData['LAUNCH']
                    self.qdm = jsonData['QDM']
                    self.abort = jsonData['ABORT']
                    self.stab = jsonData['STAB']
                except Exception as e:
                    print("Ground Station did not append state attributes to data")
                    logging.error("Ground Station did not append state attributes to data")

                self.saveState()
            else:
                jsonData['LAUNCH'] = self.launch
                jsonData['QDM'] = self.qdm
                jsonData['ABORT'] = self.abort
                jsonData['STAB'] = self.stab

            logging.info("Sent: " + data)
            print(type(data))
            self.socket.send(data.encode('ascii'))
            print("Sent");
            return 1

        except KeyboardInterrupt:
            print ("interrupt received. shutting down.")
            self.sock.close()
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
        state['STAB'] = self.stab

        try:
            logging.info(state)
            message = str.encode(state)
            # self.sock.send(pmt.serialize_str(pmt.to_pmt(message)))
            self.socket.send(message)
            logging.debug("State sent")
            return 1

        except KeyboardInterrupt:
            print ("interrupt received. shutting down.")
            self.sock.close()
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

    def getStabFlag(self):
        return self.stab


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
        state['STAB'] = self.stab

        with open('state.json', 'w+', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=4)

    def close(self):
        try:
            self.sock.close()
        except Exception as e:
            print(e)
            logging.error(e)
