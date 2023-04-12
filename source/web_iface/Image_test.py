#!/usr/bin/env python

from picamera import PiCamera
import time
import os
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

test_image = '/home/pi/testimage.jpg'

# create an instance of MinionToolbox()
minion_tools = MinionToolbox()

# Get a dictionary of the pin definitions and an instance of RPi-GPIO
GPIO, pin_defs_dict = minion_tools.config_gpio()

# Load the Minion Configuration
minion_mission_config = minion_tools.read_mission_config()

# Display the Minion Serial Number
print('Minion Serial Number: {}'.format(minion_mission_config['Minion_ID']))


def picture():
    try:
        # Collect time value from pickle on desktop
        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.HIGH)
        camera.resolution = (2592, 1944)
        camera.framerate = 15
        camera.start_preview()
        time.sleep(10)
        camera.capture(test_image)
        time.sleep(5)
        camera.stop_preview()
        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)
    except:
        print("Camera error")
        camera.stop_preview()
        GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)


if __name__ == '__main__':

    # First, remove any old test images.
    try:
        os.remove(test_image)
    except FileNotFoundError:
        pass
    camera = PiCamera()
    picture()
