#!/usr/bin/python3

import tsys01
import ms5837
from kellerLD import KellerLD
import time
import os
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

DATA_TYPE = '$02'  # Time-Lapse Sampling Type Data

NumSamples = 0

samp_count = 1

# create an instance of MinionToolbox()
minion_tools = MinionToolbox()

# Load the Minion Configuration
minion_mission_config = minion_tools.read_mission_config()

# Load the Data Configuration Directory
data_config = minion_tools.read_data_config()

# Get the current time stamp information
samp_time = minion_tools.read_timestamp()  # Use when DS3231 is not enabled in config.txt

# Get the current sample number
samp_num = minion_tools.read_samp_num()

# Minion Mission Configuration file
configLoc = '{}/Minion_config.ini'.format(data_config['Data_Dir'])

# The name of this script, used for abort_mission
current_script_name = os.path.basename(__file__)

scriptNames = ["Minion_image.py", "Minion_image_IF.py", "OXYBASE_RS232.py",
               "Recovery_Sampler_Burn.py", "OXYBASE_RS232_IF.py"]

Sf = 1/minion_mission_config['TLPsamp_tempPress_rate']

TotalSamples = minion_mission_config['TLPsamp_burst_minutes'] * 60 * minion_mission_config['TLPsamp_tempPress_rate']

# for dataNum in os.listdir('{}/minion_data/'.format(data_config['Data_Dir'])):
#     if dataNum.endswith('_TEMPPRES.txt'):
#         samp_count = samp_count + 1

samp_count_leading_zeros = "%03d" % samp_count

samp_time = "{}-{}".format(samp_count_leading_zeros, samp_time)  # Add leading zeros to sample count

file_name = "{}_TEMPPRES.txt".format(samp_time)
file_path_name = "{}/minion_data/".format(data_config['Data_Dir']) + file_name

if minion_mission_config['iniP30']:

    Psensor = ms5837.MS5837_30BA()  # Default I2C bus is 1 (Raspberry Pi 3)

    if not Psensor.init():
        print("Failed to initialize P30 sensor!")
        exit(1)

    depth_factor = .01
    surface_offset = 10

    # We have to read values from sensor to update pressure and temperature
    if Psensor.read():
        Pres_ini = round((Psensor.pressure() * depth_factor) - surface_offset, 3)
    else:
        Pres_ini = "Broken"

if minion_mission_config['iniP100']:

    Psensor = KellerLD()

    if not Psensor.init():
        print("Failed to initialize P100 sensor!")
        exit(1)

    depth_factor = 10
    surface_offset = 0

    # We have to read values from sensor to update pressure and temperature
    if Psensor.read():
        Pres_ini = round((Psensor.pressure() * depth_factor) - surface_offset, 3)
    else:
        Pres_ini = "Broken"

if minion_mission_config['iniTmp']:

    sensor_temp = tsys01.TSYS01()

    # We must initialize the sensor before reading it
    if not sensor_temp.init():
        print("Error initializing Temperature sensor")
        exit(1)


minion_tools.write_data_file_header(DATA_TYPE, file_path_name, file_name,
                                    minion_mission_config['TLPsamp_tempPress_rate'],
                                    minion_mission_config['iniP30'],
                                    minion_mission_config['iniP100'],
                                    minion_mission_config['iniTmp'])

# Display Readings
while NumSamples < TotalSamples:

    tic = time.perf_counter()

    print("")
    print("Time Lapse Sampling Mode")  # Indicate to the user in which mode the Minion is operating

    sensor_string = ''

    if minion_mission_config['iniP100'] or minion_mission_config['iniP30']:

        if Psensor.read():
            # shifting the decimal point out
            Ppressure = round((Psensor.pressure() * depth_factor) - surface_offset, 3)*1000
            Ppressure = "%07d" % Ppressure  # fixed field / prepending zeros
            Ptemperature = round(Psensor.temperature(), 2)*100  # shifting the decimal point out
            Ptemperature = "%04d" % Ptemperature  # fix field length by prepending zeros if necessary
            Pres_data = "{},{},".format(Ppressure, Ptemperature)
            print("Pressure sensor data: {}".format(Pres_data))
            sensor_string = "{}{}".format(sensor_string, Pres_data)

        else:
            message = 'Pressure Sensor Not Responding.'
            with open(file_path_name, "a") as file:
                file.write(message)
            minion_tools.abort_mission(message, scriptNames, current_script_name)

        if int(Ppressure)/1000 >= minion_mission_config['MAX_Depth']:
            message = 'Exceeded Depth Maximum!'
            with open(file_path_name, "a") as file:
                file.write(message)
            minion_tools.abort_mission(message, scriptNames, current_script_name)

    if minion_mission_config['iniTmp']:

        if not sensor_temp.read():
            print("Error reading sensor")
            minion_mission_config['iniTmp'] = False

        Temp_acc = round(sensor_temp.temperature(), 2)*100
        Temp_acc = "%04d" % Temp_acc  # fix field length by prepending zeros if necessary

        print("Temperature_accurate: {} C*100".format(Temp_acc))  # degrees Celsius * 100

        sensor_string = '{}{}'.format(sensor_string, Temp_acc)

    with open(file_path_name, "a") as file:
        file.write("\n{}".format(sensor_string))

    NumSamples = NumSamples + 1

    toc = time.perf_counter()

    timeS = toc - tic

    if timeS >= Sf:

        timeS = Sf

    time.sleep(Sf - timeS)
