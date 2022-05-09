#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import os
import math
import configparser
import sys
import pickle
sys.path.insert(0,'/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox


def update_time():
    try:
        samp_time = os.popen("sudo hwclock -l -r").read()
        samp_time = samp_time.split('.',1)[0]
        samp_time = samp_time.replace("  ","_")
        samp_time = samp_time.replace(" ","_")
        samp_time = samp_time.replace(":","-")

        with open("/home/pi/Documents/Minion_scripts/timesamp.pkl","wb") as firstp:
            pickle.dump(samp_time, firstp)
    except:
        print("update time failed")
    return samp_time


def read_sampcount():
    with open("/home/pi/Documents/Minion_scripts/sampcount.pkl","rb") as countp:
        sampcount = pickle.load(countp)
    return sampcount


def update_sampcount():
    with open("/home/pi/Documents/Minion_scripts/sampcount.pkl","rb") as countp:
        sampcount = pickle.load(countp)
        sampcount = sampcount + 1
    with open("/home/pi/Documents/Minion_scripts/sampcount.pkl","wb") as countp:
        pickle.dump(sampcount, countp)
    return sampcount

samp_time = update_time()

samp_count = read_sampcount()

i = 0
wifi = 22
light = 12
IO328 = 29

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(light, GPIO.OUT)
GPIO.setup(wifi, GPIO.OUT)
GPIO.setup(IO328, GPIO.OUT)
GPIO.output(IO328, 1)
GPIO.output(wifi, 1)

# create an instance of MinionToolbox()
minion_tools = MinionToolbox()
# Load the Minion Configuration
minion_mission_config = minion_tools.read_mission_config()

data_config = configparser.ConfigParser()
data_config.read('/home/pi/Documents/Minion_scripts/Data_config.ini')

IG_WIFI_Samples = (((minion_mission_config['IG_WIFI_D']*24) + minion_mission_config['IG_WIFI_H'])/minion_mission_config['Srate']) - (minion_mission_config['INIsamp_hours']/minion_mission_config['Srate'])

print("Minion Deployment Handler")
print("Time:  {}".format(samp_time))
print("Days : {}".format(minion_mission_config['Ddays']))
print("Hours: {}".format(minion_mission_config['Dhours']))
print("Sample rate (hours) - {}".format(minion_mission_config['Srate']))

TotalSamples = ((minion_mission_config['Ddays'] * 24) + minion_mission_config['Dhours']) / minion_mission_config['Srate']

if samp_count >= TotalSamples:
    RemainSamples = 0
else:
    RemainSamples = (TotalSamples - samp_count)

print("Total Cycles ------- {}".format(TotalSamples))

print("Cycles Remaining --- {}".format(RemainSamples))

if IG_WIFI_Samples >= samp_count:
    IgnoreWIFI = True
    print("Ignoring Wifi, in Mission")

else:
    IgnoreWIFI = False
    print("Searching for WIFI")

ifswitch = "sudo python /home/pi/Documents/Minion_tools/dhcp-switch.py"

iwlist = 'sudo iwlist wlan0 scan | grep -e "Minion_Hub" -e "Master_Hub"'

net_cfg = "ls /etc/ | grep dhcp"

ping_hub = "ping 192.168.0.1 -c 1"

ping_google = "ping google.com -c 1"

ps_test = "pgrep -a python"

scriptNames = ["TempPres.py", "Minion_image.py", "Minion_image_IF.py",
               "OXYBASE_RS232.py", "ACC_100Hz.py", "Initial_Sampler.py",
               "Recovery_Sampler_Burn.py", "TempPres_IF.py", "OXYBASE_RS232_IF.py",
               "ACC_100Hz_IF.py", "Iridium_gps.py", "Iridium_data.py",
               "xmt_minion_data.py"]

if __name__ == '__main__':

    if samp_count == 0:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/Initial_Sampler.py &')

    elif samp_count >= TotalSamples + 1 or minion_mission_config['Abort'] == True:
        GPIO.output(IO328, 0)
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/Recovery_Sampler_Burn.py &')

    else:
        if minion_mission_config['iniImg'] == True:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/Minion_image.py &')

        if minion_mission_config['iniP30'] == True or minion_mission_config['iniP100'] == True or minion_mission_config['iniTmp'] == True:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/TempPres.py &')

        if minion_mission_config['iniO2'] == True:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/OXYBASE_RS232.py &')

        if minion_mission_config['iniAcc'] == True:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/ACC_100Hz.py &')

    time.sleep(5)

    update_sampcount()
    
    #Check for WiFi while any of the scripts in scriptNames are executing
    while(any(x in os.popen(ps_test).read() for x in scriptNames)) == True:
        if minion_tools.check_wifi(IgnoreWIFI) == "Connected":
            minion_tools.kill_sampling(scriptNames)
            minion_tools.flash(2, 250, 250)
            exit(0)
        else:
            print("Sampling")
            time.sleep(5)

    #Once we get here, there are none of the scripts in scriptNames are running.  
    print('Goodbye')
    GPIO.output(wifi, 0)
    time.sleep(5)
    os.system('sudo shutdown now')
