#!/usr/bin/env python
from picamera import PiCamera
import time
import os
import sys
import argparse
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox


def picture(sample_number, sample_idx, sample_mode, data_directory):
    try:
        # samp_time = minion_tools.update_timestamp()  # Use when DS3231 is not enabled in config.txt
        # samp_count = str(len(os.listdir("{}/minion_pics/".format(data_config['Data_Dir']))) + 1)
        # samp_time = "{}-{}".format(samp_count, samp_time)

        # sample_idx = 1
        sample_time = minion_tools.update_timestamp()  # Use when DS3231 is not enabled in config.txt
        file_name = '{}-{}-{}_{}.jpg'.format(sample_number, ('%03d' % sample_idx), sample_time, sample_mode)
        file_path_name = data_directory + file_name
        # print(file_name)
        # print(file_path_name)

        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.HIGH)
        camera.resolution = (2592, 1944)
        camera.framerate = 15
        camera.start_preview()
        time.sleep(10)
        camera.capture(file_path_name)
        time.sleep(5)
        camera.stop_preview()
        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)
        print("[ IMG ] {}".format(file_name))

    except:
        print("Camera error")
        camera.stop_preview()
        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)


# Initializations
samp_counter = 0

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

# Get the current time stamp information
samp_time = minion_tools.update_timestamp()

# Get the current sample number
samp_num = minion_tools.read_samp_num()

# Create an instance of the argument parser
parser = argparse.ArgumentParser()

# Add Arguments:
parser.add_argument('--mode', help='Sampling Mode: TEST, INI, TLP or FIN')

# Parse the arguments
args = parser.parse_args()

# Set up sampling and data logging based on sampling mode
if args.mode.upper() == 'TEST':  # TODO: Implement Test Mode
    # test_sensor()
    print('Test Mode')
    exit(0)

elif args.mode.upper() == 'INI':
    print('[ IMG ] Initial Sampling Mode')

    sample_period = minion_mission_config['INIsamp_camera_period']
    total_samples = (minion_mission_config['INIsamp_hours'] * 60) / sample_period

    samp_num_leading_zeros = "%03d" % samp_num

    mode_str = 'IMG-INI'

    directory = '{}/minion_data/INI/'.format(data_config['Data_Dir'])

elif args.mode.upper() == 'TLP':
    print('[ IMG ] Time Lapse Sampling Mode')

    sample_period = minion_mission_config['TLPsamp_camera_period']
    total_samples = minion_mission_config['TLPsamp_burst_minutes'] / sample_period

    samp_num_leading_zeros = "%03d" % samp_num

    mode_str = 'IMG-TLP'

    directory = '{}/minion_pics/'.format(data_config['Data_Dir'])

elif args.mode.upper() == 'FIN':
    print('[ IMG ] Final Sampling Mode')

    sample_period = minion_mission_config['FINsamp_camera_period']
    total_samples = (minion_mission_config['FINsamp_hours'] * 60) / sample_period

    samp_num_leading_zeros = "%03d" % samp_num

    mode_str = 'IMG-FIN'

    directory = '{}/minion_data/FIN/'.format(data_config['Data_Dir'])

else:
    print('[ IMG ] Unknown Sample Mode.  Exiting.')
    sample_period = 0
    total_samples = 0
    samp_num_leading_zeros = 0
    exit(0)

sample_period_secs = sample_period * 60

if __name__ == '__main__':

    camera = PiCamera()

    while samp_counter < total_samples:

        tic = time.perf_counter()

        # Increment the sample number
        samp_counter += 1

        picture(samp_num_leading_zeros, samp_counter, mode_str, directory)

        timeS = time.perf_counter() - tic

        if timeS >= sample_period_secs:
            timeS = sample_period_secs

        time.sleep(sample_period_secs - timeS)


