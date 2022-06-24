from ECE16Lib.Communication import Communication
from ECE16Lib.CircularList import CircularList
from ECE16Lib.HRMonitor import HRMonitor
from ECE16Lib.Pedometer import Pedometer
import pyowm
from pyowm import OWM
import os
from matplotlib import pyplot as plt
import numpy as np
import datetime
from time import time


if __name__ == "__main__":


    process_time = 1  # compute the step count every second


    strsteps = '0'
    strjumps = '0'

    fs = 50                         # sampling rate of 50Hz
    num_samples = 500               # 10 seconds of data @ 50Hz
    refresh_time = 1                # compute the heart rate every second
    heartppg = 0                    # this is where we will store our heart rate data from arduino
    timeppg = 0                     # this is where we will store our time data from arduino

    #initiliaze our circularlists to hold heart rate and time data
    ped = Pedometer(num_samples, fs, [])
    ppg = CircularList([], num_samples)
    times = CircularList([], num_samples)
    
    #initliaze connection to arduino
    comms = Communication('COM4', 115200)
    comms.clear()                   # just in case any junk is in the pipes
    comms.send_message("wearable")  # begin sending data
    # create our hearmonitor object
    heart = HRMonitor(num_samples, fs, [])
    while(True):
        message = comms.receive_message()
        if (message != None):
            message = message.strip()
            print(message) 
            # if we receive weather from the arduino we want to display the weather and time

            # if we receive steps from the arduino we want to start processing the step information and displaying
            if (str(message) == "Steps"):
                    previous_time = time()
                    while (str(message) != "Heart"):
                        message = comms.receive_message() 
                        if (message != None):
                            #print(message)
                            try:
                                (m1, m2, m3, m4) = message.split(',')
                            except ValueError:  # if corrupted data, skip the sample
                                continue
                            # Collect data in the pedometer
                            ped.add(int(m2), int(m3), int(m4))
                            
                            # if data is available to send, send data
                            current_time = time()
                            if (current_time - previous_time > refresh_time):
                                previous_time = time()
                                print('WE MADE IT TO RIGHT HERE')
                                steps, f, peaks, filtered = ped.process()

                                steps, peaks, filtered = ped.process()
                                print("Step count: {:d}".format(steps))
                                strsteps = str(steps)

                                comms.send_message(strsteps)
                                last_str = strsteps                 
            # if we receive heart from the arduino we want to start processing the heart information and displaying
            if (str(message) == "Heart"):
                    previous_time = time()
                    while(str(message) != "Weather"):
                        #receive message from the arduino
                        message = comms.receive_message()
                        if(message != None):
                            print(message)
                            try:
                                #receive the raw data from arduino
                                (timeppg, heartppg) = message.split(',')
                            except ValueError:
                                continue
                            #add our data to circular list
                            ppg.add(int(heartppg))
                            times.add(int(timeppg))

                            # update our OLED with current heart rate once a second
                            current_time = time()
                            
                            if (current_time - previous_time > refresh_time):
                                previous_time = current_time
                                #update our heart rate object with our listed data
                                heart.add(times,ppg)
                                try:
                                    #filter and process our data
                                    hr, peaks, filtered =  heart.process()
                                    #heart rate needs to be an int and scaled up
                                    hr = int(hr*1000)
                                    output = hr
                                    # if our hr is too high or low than the watch is not attached. or they dead
                                    if (hr > 250 or hr < 20):
                                        output = "N/A"
                                    print("Your heart rate is currently: ", output)
                                    #send heart rate data to arduino
                                    comms.send_message(str(output))
                                except:
                                    continue
            else:
                try: 
                    print("WE ENTERED WEATHER")
                    owm = OWM('4f1f4c6040e4ec94f3809aaba5c6f914').weather_manager()
                    weather = owm.weather_at_place('San Diego,CA,US').weather
                    print(weather.temperature('fahrenheit'))
                    dt = datetime.datetime.now()
                    # w = weather.get_weather()
                    temp = weather.temperature('fahrenheit')

                    while (str(message) != "Steps"):
                        try: 
                            print("I am in this loop but not sending anything")
                            comms.send_message(dt.strftime("%X\n"))
                            message = comms.receive_message()
                            message = message.strip()
                            print(message)
                        except:
                            continue
                except:
                    continue

    print("Closing connection. ")
    comms.send_message("sleep")
    comms.close()