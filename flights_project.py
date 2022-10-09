"""
Written by Mina Basem, GitHub Profile: https://github.com/MinaBasem
"""

import pathlib
import datetime
import requests
from FlightRadar24.api import FlightRadar24API
from bs4 import BeautifulSoup
import numpy as np
import time
import matplotlib.pyplot as plt

fr_api = FlightRadar24API()
telemetry_altitude = 0
telemetry_ground_speed = 1
arrival_airport = ''
departure_airport = ''
flight_reg = 'SU-GEE'       # CHANGE THIS TO DESIRED AIRCRAFT REGISTRATION
airline_icao = 'MSR'        # CHANGE THIS TO THE DESIRED AIRLINE

def import_flight_data():  
    """
    Obtains flight data that is web-scraped using beautiful soup from FlightRadar's aircraft activity list
    Checks whether an aircraft is currently live (visible in real time) on the website
    Imported data is then saved to html-content.txt
    """
    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)
    beautifulsoup_URL = "https://www.flightradar24.com/data/aircraft/{}".format(flight_reg)
    fake_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15' 
    }   # fake header tricks FlightRadar into thinking an actual browser is viewing it's page, this block wouldn't work without it
    page = requests.get(beautifulsoup_URL, headers=fake_headers)
    soup = BeautifulSoup(page.content, "html.parser")
    flightradar_list_html = soup.find(id="tbl-datatable")   #this is the extracted table with id = tbl-datatable
    flightradar_list = str(flightradar_list_html.find('tr', class_='live data-row'))
    with open("/Users/Mina/Desktop/flights_project/html_content.txt", 'w') as html_content:
        html_content.write(str(flightradar_list))

    indexes = np.array(list(find_all(flightradar_list, '/data/airports/')))
    indexes = indexes + 15
    print(indexes) #returns all link indexes

    arrival_airport = list(flightradar_list)[indexes[0]] + list(flightradar_list)[indexes[0]+1] + list(flightradar_list)[indexes[0]+2]
    print('\nArrival Airport: ' + arrival_airport.upper())
    
    departure_airport = list(flightradar_list)[indexes[2]] + list(flightradar_list)[indexes[2]+1] + list(flightradar_list)[indexes[2]+2]
    print('Departure Airport: ' + departure_airport.upper())
    

    if 'live data-row' in str(flightradar_list_html):
        isActive = True
        print('\n----> Aircraft is online')
    else:
        isActive = False
        print('----> Aircraft is offline')

    print('----> Successfuly imported flight data')
        
    
def obtain_telemetry(flight_reg):          # Done using FlightRadar API obtained from https://github.com/JeanExtreme002/FlightRadarAPI

    now = datetime.datetime.now()
    now = now - datetime.timedelta(microseconds=now.microsecond)
    airline = airline_icao
    flights = fr_api.get_flights(airline = airline)
    data_str = str(flights)
    data_clean = data_str.replace(', ', '\n')
    data_clean = data_clean.replace('[', '')
    data_clean = data_clean.replace(']', '')
    data_clean = data_clean.replace('<', (str(now) + ' '))
    data_clean = data_clean.replace('>', '')

    with open("live_flight_data.txt", 'w') as data_file:
        data_file.write(data_clean)

    with open("live_flight_data.txt", 'r') as data_file:
        lines = data_file.read().splitlines()

    for line in lines:
        if flight_reg in line:
            print('\n' + '------>' + line)
            flight_line = line

    indiv_data_list = flight_line.strip().split(' - ')
    print('---->'  + str(indiv_data_list) + '\n')
    for i in range(1, 3):
        print(indiv_data_list[i])  #Prints the alt and gdspeed text
    print('\n')

    telemetry_altitude = int(indiv_data_list[1][10:])         #in feet
    telemetry_ground_speed = int(indiv_data_list[2][14:])     #in miles/hour

    exactTime = now - datetime.timedelta(microseconds=now.microsecond)
    print(str(exactTime) + ',' + str(telemetry_altitude) + ',' + str(telemetry_ground_speed))

    with open("telemetry_file.txt", 'a') as telemetry_file:
        exactTime = now - datetime.timedelta(microseconds=now.microsecond)
        telemetry_file.write(str(exactTime) + ',' + str(telemetry_altitude) + ',' + str(telemetry_ground_speed) + '\n')

    print('----> ' + 'Aircraft is visible on API')


def visualize_data(file):
    altitude_nparray = np.array([])
    gdspeed_nparray = np.array([])
    altitude = []
    altitude_element = []
    ground_speed = []
    ground_speed_element = []
    time = []
    time_element = []
    with open(file, 'r') as telemetry_file:
        number_of_lines = 0
        for line in telemetry_file:
            number_of_lines = number_of_lines + 1   #lines counter
            line_as_list = str(line)                #convert str to list
            indexes = np.array(list(find_all(line, ',')))

            for char in line_as_list[indexes[0]+1:indexes[1]-1]:    #obtains altitude value between the 2 commas
                altitude_element.append(char)
            altitude_element_string = listToString(altitude_element)
            altitude_nparray = np.append(altitude_nparray, int(altitude_element_string))
            altitude_element.clear()
            #print(altitude_nparray)

            for char in line_as_list[indexes[1]+1:]:                    #obtains ground speed after 2nd comma
                ground_speed_element.append(char)
            ground_speed_element_string = listToString(ground_speed_element)
            gdspeed_nparray = np.append(gdspeed_nparray, int(ground_speed_element_string))
            ground_speed_element.clear()
            #print(gdspeed_nparray)

        x_axis_value = np.array(range(0, number_of_lines))
        altitude_axis_value = np.array(altitude_nparray)
        groundspeed_axis_value = np.array(gdspeed_nparray)

        fig,ax = plt.subplots()
        ax.plot(x_axis_value, altitude_axis_value, color='steelblue', linewidth = 2)
        ax.set_xlabel('Time', fontsize=14)                                          #add x-axis label
        ax.set_ylabel('Altitude', color='steelblue', fontsize=10)                   #add y-axis label
        ax2 = ax.twinx()                                                            #define second y-axis that shares x-axis with current plot
        ax2.plot(x_axis_value, groundspeed_axis_value, color='red', linewidth = 2)  #add second line to plot
        ax2.set_ylabel('Ground Speed', color='red', fontsize=10)                    #add second y-axis label
        plt.title('Telemetry for Aircraft Reg.: {}'.format(flight_reg))
        plt.show()



def find_all(string, match):            #find indexes
                start = 0
                while True:
                    start = string.find(match, start)
                    if start == -1: return
                    yield start
                    start += len(match)

def listToString(s):
    str = ""
    for element in s:
        str += element
    return str

# RUNNING THE FUNCTIONS FROM HERE
"""
while telemetry_ground_speed != 0:
    if arrival_airport and departure_airport == '':
        try:
            import_flight_data()
        except:
            obtain_telemetry(flight_reg)
            time.sleep(5)
"""
visualize_data('telemetry_file.txt')
