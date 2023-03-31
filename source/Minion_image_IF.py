#!/usr/bin/python3
from picamera import PiCamera
import time
import os
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

NumSamples = 0
samp_count = 1

sampNum = [0]

camera = PiCamera()

# create an instance of MinionToolbox()
minion_tools = MinionToolbox()

# Get a dictionary of the pin definitions and an instance of RPi-GPIO
GPIO, pin_defs_dict = minion_tools.config_gpio()

# Load the Minion Configuration
minion_mission_config = minion_tools.read_mission_config()

# Load the Data Configuration Directory
data_config = minion_tools.read_data_config()

# Minion Mission Configuration file
configLoc = '{}/Minion_config.ini'.format(data_config['Data_Dir'])

# Initial Samples will be performed if pictures have not been performed during Time Lapse mode
if len(os.listdir('{}/minion_pics'.format(data_config['Data_Dir']))) == 0:

    Srate = minion_mission_config['FINsamp_camera_rate']
    TotalSamples = minion_mission_config['INIsamp_hours']*(60/minion_mission_config['INIsamp_camera_rate'])
    # Srate = float(config['Initial_Samples']['Camera_sample_rate'])
    RECOVER = 0
    mode = 'Initial'

    for dataNum in os.listdir('{}/minion_data/INI/'.format(data_config['Data_Dir'])):
        if dataNum.endswith('_Pic-INI.jpg'):
            sampNum.append(int(dataNum.split("-", 1)[0]))

# Final Samples will be performed
else:

    Srate = minion_mission_config['FINsamp_camera_rate']
    TotalSamples = minion_mission_config['FINsamp_hours'] * (60 / Srate)
    RECOVER = 1
    mode = 'Final'

    for dataNum in os.listdir('{}/minion_data/FIN/'.format(data_config['Data_Dir'])):
        if dataNum.endswith('_Pic-FIN.jpg'):
            sampNum.append(int(dataNum.split("-", 1)[0]))

samp_count = max(sampNum) + 1    


def picture(config_dir, num_samples, samp_mode):
    try:
        print("Sample Mode: " + mode)

        # Update the time stamp
        samp_time = minion_tools.update_timestamp()  # Use when DS3231 is not enabled in config.txt
        # print('Time Stamp: ' + str(samp_time))

        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.HIGH)
        camera.resolution = (2592, 1944)
        camera.framerate = 15
        camera.start_preview()
        time.sleep(10)

        if samp_mode == 'Initial':
            samp_time = "{}-{}-{}".format(samp_count, num_samples, samp_time)
            camera.capture('{}/minion_data/INI/{}_Pic-INI.jpg'.format(config_dir, samp_time))

        if samp_mode == 'Final':
            samp_time = "{}-{}-{}".format(samp_count, num_samples, samp_time)
            camera.capture('{}/minion_data/FIN/{}_Pic-FIN.jpg'.format(config_dir, samp_time))
        
        time.sleep(1)
        print("Image : {}".format(samp_time))
        camera.stop_preview()
        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)

    except:
        camera.stop_preview()
        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)
        print("Camera Error")


while NumSamples <= TotalSamples:

    tic = time.perf_counter()

    picture(data_config['Data_Dir'], NumSamples, mode)

    NumSamples = NumSamples + 1

    toc = time.perf_counter()

    timeS = toc - tic

    if timeS >= Srate * 60:

        timeS = Srate

    time.sleep((Srate*60) - timeS)
