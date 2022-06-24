from WatchLib.Communication import Communication
from WatchLib.CircularList import CircularList
from matplotlib import pyplot as plt
from time import time
import numpy as np

"""
A class to provide a circular list structure that maintains its length as
elements are added to it.
"""
class IdleDetector:
    message = ""
    __serial_name = ""
    __baud_rate = 115200
    __ser = None
    def __init__(self, serial_name=None, baud_rate=None):
        self.__serial_name = serial_name
        self.__baud_rate = baud_rate
        if(serial_name != None and baud_rate != None):
            self.setup()

        super().__init__(data)
    def send_message(self, message):
        if (message[-1] != '\n'):
            message = message + '\n'
        self.__ser.write(message.encode('utf-8'))
    def stream_data(self):

    def detect_activity(self, ax):
        person_state = 'active'
        if ((ax[-1] < 2650) & (person_state == 'active')):
                person_state = 'inactive'
                comms.send_message(person_state)

        if ((ax[-1] > 2650) & (person_state == 'inactive')):
            person_state = 'active'
            comms.send_message(person_state)

