#!/usr/bin/env python3
from picamera import PiCamera
import time
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox


def picture():
    try:
        camera.resolution = (2592, 1944)
        camera.framerate = 15
        camera.start_preview()
        time.sleep(10)
        camera.capture('/home/pi/M{}-test.jpg'.format(minion_mission_config['Minion_ID']))
        time.sleep(5)
        camera.stop_preview()
    except:
        print("Camera error")


# create an instance of MinionToolbox()
minion_tools = MinionToolbox()

# Get a dictionary of the pin definitions and an instance of RPi-GPIO
GPIO, pin_defs_dict = minion_tools.config_gpio()

# Load the Minion Configuration
minion_mission_config = minion_tools.read_mission_config()

print("Minion Serial Number: {}".format(minion_mission_config['Minion_ID']))


if __name__ == '__main__':

    camera = PiCamera()
    GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.HIGH)
    picture()
    GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)
