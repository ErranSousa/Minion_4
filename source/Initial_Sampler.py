#!/usr/bin/env python3

import RPi.GPIO as GPIO
import tsys01
import ms5837
from kellerLD import KellerLD
import pickle
import time
import os
import math
import configparser
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

DATA_TYPE = '$01'  # Initial Sampling Type Data

BURN = 33
data_rec = 16

samp_count = 1

NumSamples = 0

IO328 = 29

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BURN, GPIO.OUT)
GPIO.setup(data_rec, GPIO.OUT)
GPIO.output(BURN, 0)
GPIO.output(data_rec, 1)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def kill_sampling(scriptNames):
    for script in scriptNames:
        os.system("sudo pkill -9 -f {}".format(script))


def abortMission(configLoc):
    kill_sampling(scriptNames)

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


minion_tools = MinionToolbox()  # create an instance of MinionToolbox() called minion_tools

scriptNames = ["TempPres.py", "Minion_image.py", "Minion_image_IF.py", "OXYBASE_RS232.py", "ACC_100Hz.py",
               "TempPres_IF.py", "OXYBASE_RS232_IF.py", "ACC_100Hz_IF.py", "Iridium_gps.py", "Iridium_data.py"]

data_config = configparser.ConfigParser()
data_config.read('/home/pi/Documents/Minion_scripts/Data_config.ini')

configDir = data_config['Data_Dir']['Directory']
configLoc = '{}/Minion_config.ini'.format(configDir)
config = configparser.ConfigParser()
config.read(configLoc)
MAX_Depth = float(config['Mission']['Max_Depth'])
# MAX_Depth = MAX_Depth*100.4  # Convert from meters to mBar
Abort = str2bool(config['Mission']['Abort'])
iniImg = str2bool(config['Sampling_scripts']['Image'])
iniP30 = str2bool(config['Sampling_scripts']['30Ba-Pres'])
iniP100 = str2bool(config['Sampling_scripts']['100Ba-Pres'])
iniTmp = str2bool(config['Sampling_scripts']['Temperature'])
iniO2 = str2bool(config['Sampling_scripts']['Oxybase'])
iniAcc = str2bool(config['Sampling_scripts']['ACC_100Hz'])

if Abort == True:
    GPIO.setup(29, GPIO.OUT)
    GPIO.output(29, 0)
    os.system('sudo python3 /home/pi/Documents/Minion_scripts/Recovery_Sampler_Burn.py &')

# firstp = open("/home/pi/Documents/Minion_scripts/timesamp.pkl","rb")
with open("/home/pi/Documents/Minion_scripts/timesamp.pkl", "rb") as firstp:
    samp_time = pickle.load(firstp)

for dataNum in os.listdir('{}/minion_data/INI/'.format(configDir)):
    if dataNum.endswith('_TEMPPRES-INI.txt'):
        samp_count = samp_count + 1

samp_count_leading_zeros = "%03d" % samp_count

# samp_time = "{}-{}".format(samp_count, samp_time)
samp_time = "{}-{}".format(samp_count_leading_zeros, samp_time)  # Add leading zeros to sample count

Stime = float(config['Initial_Samples']['hours'])
Srate = float(config['Initial_Samples']['TempPres_sample_rate'])

file_name = "{}_TEMPPRES-INI.txt".format(samp_time)
# file_path_name = "{}/minion_data/INI/{}_TEMPPRES-INI.txt".format(configDir, samp_time)
file_path_name = "{}/minion_data/INI/".format(configDir) + file_name

Sf = 1 / Srate

TotalSamples = Stime * 60 * 60 * Srate

######################

time.sleep(1)

# file = open(file_path_name,"a+")
# with open(file_path_name,"a+") as file:

# Prepare the Header Record
# file.write(DATA_TYPE) #Write Data Type Identifier
# file.write("{}_TEMPPRES.txt ".format(samp_time))
# file.write("," + file_name)  #Write the file name
# file.write("," + str(Srate)  #Write the sample rate

if iniP30 == True:

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

    # file.write("Pressure(dbar),Temp(C)")
    # file.write(",Pressure(dbar*1000),Temp(C*100)")  #Meta-Record for fixed field Press and Temp

if iniP100 == True:

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

    # file.write("Pressure(dbar),Temp(C)")
    # file.write(",Pressure(dbar*1000),Temp(C*100)")  #Meta-Record for fixed field Press and Temp

if iniTmp == True:

    sensor_temp = tsys01.TSYS01()

    # We must initialize the sensor before reading it
    if not sensor_temp.init():
        print("Error initializing Temperature sensor")
        exit(1)

    # file.write(", TempTSYS01(C)")
    # file.write(",TempTSYS01(C*100)")

# file.write("\n")
# file.close()

# Write a header to the data file
minion_tools.write_data_file_header(DATA_TYPE, file_path_name, file_name, Srate, iniP30, iniP100, iniTmp)

if __name__ == '__main__':

    if iniImg == True:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/Minion_image_IF.py &')

    if iniO2 == True:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/OXYBASE_RS232_IF.py &')

    if iniAcc == True:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/ACC_100Hz_IF.py &')

    # Spew readings
    while NumSamples <= TotalSamples:

        tic = time.perf_counter()

        print("Initial Sampling Mode")  # Indicate to the user in which mode the Minion is operating

        # file = open(file_path_name,"a")

        sensor_string = ''

        if iniP100 or iniP30 == True:

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
                print('Pressure Sensor ded')
                with open(file_path_name, "a") as file:
                    file.write('Pressure Sensor fail')
                abortMission(configLoc)

            print("Depth: " + str(int(Ppressure) / 1000))  # TESTING ONLY

            # if Ppressure >= MAX_Depth:
            if int(Ppressure) / 1000 >= MAX_Depth:
                with open(file_path_name, "a") as file:
                    file.write("Minion Exceeded Depth Maximum!")
                abortMission(configLoc)

        if iniTmp == True:

            if not sensor_temp.read():
                print("Error reading sensor")
                iniTmp = False

            # Temp_acc = round(sensor_temp.temperature(),4)
            Temp_acc = round(sensor_temp.temperature(), 2) * 100
            Temp_acc = "%04d" % Temp_acc

            # print("Temperature_accurate: {} C".format(Temp_acc))
            print("Temperature_accurate: {} C*100".format(Temp_acc))  # degrees Celsius * 100

            sensor_string = '{}{}'.format(sensor_string, Temp_acc)

        with open(file_path_name, "a") as file:
            # file.write("{}\n".format(sensor_string))
            file.write("\n{}".format(sensor_string))

        NumSamples = NumSamples + 1

        toc = time.perf_counter()

        timeS = toc - tic

        if timeS >= Sf:
            timeS = Sf

        time.sleep(Sf - timeS)

    # file.close()
    kill_sampling(scriptNames)
    GPIO.setup(data_rec, GPIO.OUT)
    GPIO.output(data_rec, 0)
