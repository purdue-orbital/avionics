import zmq
import _thread as thread
import os
import json
import logging
import socket
import time

class Radio:
    def __init__(self, DEBUG = 0, isGroundStation = False, hostname = '127.0.0.1'):
        """
        DEBUG 0 is for communication between two computers, for which hostname must also be defined. DEBUG 1 is for local communication uses localhost hostname.
        """
        self.launch = False
        self.qdm = False
        self.abort = False
        self.stab = False

        self.DEBUG = DEBUG
        self.isGroundStation = isGroundStation
        self.hostname = (hostname)
        self.queue = None

        logging.basicConfig(level=(logging.INFO, logging.DEBUG)[self.DEBUG > 0], filename='mission.log', format='%(asctime)s %(levelname)s:%(message)s')

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
                    if self.isGroundStation:
                        if self.launch != jsonData['LAUNCH'] or self.qdm != jsonData['QDM'] or self.abort != jsonData['ABORT'] or self.stab != jsonData['STAB']:
                            logging.warning("State mismatch, resending state")
                            # TODO Send State
                    else:
                        #DEBUG
                        if self.launch != jsonData['LAUNCH'] or self.qdm != jsonData['QDM'] or self.abort != jsonData['ABORT'] or self.stab != jsonData['STAB']:
                            logging.info("State Updated:\nLaunch {0}\nQDM {1}\nAbort {2}\nStability {3}".format(jsonData['LAUNCH'], jsonData['QDM'], jsonData['ABORT'], jsonData['STAB']))

                        self.launch = jsonData['LAUNCH']
                        self.qdm = jsonData['QDM']
                        self.abort = jsonData['ABORT']
                        self.stab = jsonData['STAB']

                    if self.queue is not None:
                        self.queue.append(message)
                    else:
                        print("Queue unbound")
                        logging.error("Queue unbound")    
                except Exception as e:
                    print("Invalid message received")
                    logging.error(e)

        try: 
            if not self.isGroundStation:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind((('127.0.0.1', socket.gethostname()) [self.DEBUG != 1], 5000))
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.hostname, 5000))

            thread.start_new_thread(receive, ())
        except Exception as e:
            print(e)
            print("test")


    def send(self, data):
        """
        Sends JSON formatted data to the socket attached to radio interface.
        For single variable values, do not exceed one layer of depth.
        For multi-variable values, do not exceed two layers of depth.

        JSON formatting is maintained by Matt Drozt. TODO: Example will be included at a later date.

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
            else:
                jsonData['LAUNCH'] = self.launch
                jsonData['QDM'] = self.qdm
                jsonData['ABORT'] = self.abort
                jsonData['STAB'] = self.stab

            logging.info("Sent: " + data)
            self.socket.send(data.encode('ascii'))
            print("Sent");
            return 1

        except KeyboardInterrupt:
            print ("interrupt received. shutting down.")
            self.sock.close()
            exit()

        except Exception as e:
            print("Here" + e)
            logging.error(e)
            return 0

    def bindQueue(self, queue):
        """
        Supply a queue reference for data placement. See recvTest.py for example usage.
        """
        self.queue = queue

    def getLaunchFlag(self):
        return self.launch

    def getQDMFlag(self):
        return self.qdm

    def getAbortFlag(self):
        return self.abort

    def getStabFlag(self):
        return self.stab