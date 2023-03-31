#!/usr/bin/env python
from picamera import PiCamera
import time
import os
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

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


def picture():
    try:
        print("Sample Mode: Time-Lapse")
        samp_time = minion_tools.update_timestamp()  # Use when DS3231 is not enabled in config.txt
        samp_count = str(len(os.listdir("{}/minion_pics/".format(data_config['Data_Dir']))) + 1)
        samp_time = "{}-{}".format(samp_count, samp_time)
        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.HIGH)
        camera.resolution = (2592, 1944)
        camera.framerate = 15
        camera.start_preview()
        time.sleep(10)
        camera.capture('{}/minion_pics/{}.jpg'.format(data_config['Data_Dir'], samp_time))
        time.sleep(5)
        camera.stop_preview()
        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)
        print("Image : {}".format(samp_time))

    except:
        print("Camera error")
        camera.stop_preview()
        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)


if __name__ == '__main__':

    camera = PiCamera()
    picture()

