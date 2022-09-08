#!/usr/bin/env python

from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import os
import configparser

test_image = '/home/pi/testimage.jpg'

data_config = configparser.ConfigParser()
data_config.read('/home/pi/Documents/Minion_scripts/Data_config.ini')

configDir = data_config['Data_Dir']['Directory']
configLoc = '{}/Minion_config.ini'.format(configDir)
config = configparser.ConfigParser()
config.read(configLoc)

mNumber = config['MINION']['Number']
print(mNumber)

GPIO.setwarnings(False)

i = 0
light = 12
power = 32

def flash():
    j = 0
    while j <= 1:
        GPIO.output(light, 1)
        time.sleep(.25)
        GPIO.output(light, 0)
        time.sleep(.25)
        j = j + 1


def picture():
    try:
        # Collect time value from pickle on desktop
        GPIO.output(light, 1)
        camera.resolution = (2592, 1944)
        camera.framerate = 15
        camera.start_preview()
        time.sleep(10)
        camera.capture(test_image)
        time.sleep(5)
    except:
        print("Camera error")


if __name__ == '__main__':

    # First, remove any old test images.
    try:
        os.remove(test_image)
    except FileNotFoundError:
        pass
    camera = PiCamera()
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(light, GPIO.OUT)
    GPIO.setup(power, GPIO.OUT)
    picture()
    camera.stop_preview()
    GPIO.output(light, 0)

