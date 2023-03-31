#!/usr/bin/env python3

import tsys01
import ms5837
from kellerLD import KellerLD
import pickle
import time
import os
import configparser
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

DATA_TYPE = '$01'  # Initial Sampling Type Data

# Initializations
samp_count = 1
NumSamples = 0

def abortMission(configLoc):
    minion_tools.kill_sampling(scriptNames)

    print("Max Depth Exceeded!")

    abortConfig = configparser.ConfigParser()
    abortConfig.read(configLoc)
    abortConfig.set('Mission', 'Abort', '1')
    with open(configLoc, 'wb') as abortFile:
        abortConfig.write(abortFile)

    GPIO.setup(29, GPIO.OUT)
    GPIO.output(29, 0)
    os.system('sudo python3 /home/pi/Documents/Minion_scripts/Recovery_Sampler_Burn.py &')

    time.sleep(60)
    exit(0)


# Create an instance of MinionToolbox()
minion_tools = MinionToolbox()  # create an instance of MinionToolbox() called minion_tools

# Configure the Raspberry Pi GPIOs
GPIO, pin_defs_dict = minion_tools.config_gpio()

# Load the Minion Configuration
minion_mission_config = minion_tools.read_mission_config()

# Load the Data Configuration Directory
data_config = minion_tools.read_data_config()

# Get the current time stamp information
samp_time = minion_tools.read_timestamp()  # Use when DS3231 is not enabled in config.txt

# Minion Mission Configuration file
configLoc = '{}/Minion_config.ini'.format(data_config['Data_Dir'])

scriptNames = ["TempPres.py", "Minion_image.py", "Minion_image_IF.py", "OXYBASE_RS232.py", "ACC_100Hz.py",
               "TempPres_IF.py", "OXYBASE_RS232_IF.py", "ACC_100Hz_IF.py", "Iridium_gps.py", "Iridium_data.py"]

print('Timestamp: {}'.format(samp_time))

if minion_mission_config['Abort']:
    # GPIO.setup(29, GPIO.OUT)
    # GPIO.output(29, 0)
    os.system('sudo python3 /home/pi/Documents/Minion_scripts/Recovery_Sampler_Burn.py &')

# firstp = open("/home/pi/Documents/Minion_scripts/timesamp.pkl","rb")
# with open("/home/pi/Documents/Minion_scripts/timesamp.pkl", "rb") as firstp:
#     samp_time = pickle.load(firstp)

for dataNum in os.listdir('{}/minion_data/INI/'.format(data_config['Data_Dir'])):
    if dataNum.endswith('_TEMPPRES-INI.txt'):
        samp_count = samp_count + 1

samp_count_leading_zeros = "%03d" % samp_count

samp_time = "{}-{}".format(samp_count_leading_zeros, samp_time)  # Add leading zeros to sample count

file_name = "{}_TEMPPRES-INI.txt".format(samp_time)
file_path_name = "{}/minion_data/INI/".format(data_config['Data_Dir']) + file_name

Sf = 1 / minion_mission_config['INIsamp_tempPres_rate']

TotalSamples = minion_mission_config['INIsamp_hours'] * 60 * 60 * minion_mission_config['INIsamp_tempPres_rate']

######################

time.sleep(1)

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

# Write a header to the data file
minion_tools.write_data_file_header(DATA_TYPE, file_path_name, file_name, minion_mission_config['Srate'], minion_mission_config['iniP30'],
                                    minion_mission_config['iniP100'], minion_mission_config['iniTmp'])

if __name__ == '__main__':

    GPIO.output(pin_defs_dict['LED_GRN'], GPIO.HIGH)

    if minion_mission_config['iniImg']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/Minion_image_IF.py &')

    if minion_mission_config['iniO2']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/OXYBASE_RS232_IF.py &')

    if minion_mission_config['iniAcc']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/ACC_100Hz_IF.py &')

    # Spew readings
    while NumSamples <= TotalSamples:

        tic = time.perf_counter()

        print("")
        print("Initial Sampling Mode")  # Indicate to the user in which mode the Minion is operating

        sensor_string = ''

        if minion_mission_config['iniP100'] or minion_mission_config['iniP30']:

            if Psensor.read():
                # Ppressure = round((Psensor.pressure() * depth_factor) - surface_offset, 3)
                Ppressure = round((Psensor.pressure() * depth_factor) - surface_offset,
                                  3) * 1000  # shifting the decimal point out
                Ppressure = "%07d" % Ppressure  # prepending zeros
                # Ptemperature = round(Psensor.temperature(),3)
                Ptemperature = round(Psensor.temperature(), 2) * 100
                Ptemperature = "%04d" % Ptemperature
                Pres_data = "{},{},".format(Ppressure, Ptemperature)
                print("Pressure sensor data: {}".format(Pres_data))
                sensor_string = "{}{}".format(sensor_string, Pres_data)

            else:
                print('Pressure Sensor not responding.')
                with open(file_path_name, "a") as file:
                    file.write('Pressure Sensor reading failure.')
                abortMission(configLoc)

            print("Depth: " + str(int(Ppressure) / 1000))  # TESTING ONLY

            # if Ppressure >= MAX_Depth:
            if int(Ppressure) / 1000 >= minion_mission_config['MAX_Depth']:
                with open(file_path_name, "a") as file:
                    file.write("Minion Exceeded Depth Maximum!")
                abortMission(configLoc)

        if minion_mission_config['iniTmp']:

            if not sensor_temp.read():
                print("Error reading sensor")
                minion_mission_config['iniTmp'] = False  # What is the purpose of this???

            Temp_acc = round(sensor_temp.temperature(), 2) * 100
            Temp_acc = "%04d" % Temp_acc

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

    minion_tools.kill_sampling(scriptNames)
    GPIO.output(pin_defs_dict['LED_GRN'], GPIO.LOW)
