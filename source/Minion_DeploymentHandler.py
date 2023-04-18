#!/usr/bin/env python3

import time
import os
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox
from minion_hat import MinionHat


def check_wifi_and_scripts(script_list):
    time.sleep(5)  # Wait for things to settle before checking for wifi & scripts
    # Check for WiFi while any of the scripts in script_list are executing
    while any(x in os.popen(ps_test).read() for x in script_list):
        if minion_tools.check_wifi(IgnoreWIFI) == "Connected":
            minion_tools.kill_sampling(script_list)
            minion_tools.flash(2, 250, 250)
            GPIO.output(pin_defs_dict['LED_GRN'], GPIO.LOW)
            GPIO.output(pin_defs_dict['LED_RED'], GPIO.HIGH)
            exit(0)
        else:
            print("Sampling")
            time.sleep(5)


def start_time_lapse_scripts():
    if minion_mission_config['iniImg']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/Minion_image.py &')

    if minion_mission_config['iniP30'] or minion_mission_config['iniP100'] or minion_mission_config['iniTmp']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/TempPres.py &')

    if minion_mission_config['iniO2']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/OXYBASE_RS232.py &')


# create an instance of MinionToolbox()
minion_tools = MinionToolbox()

# Configure the Raspberry Pi GPIOs & configure pins to their default states
GPIO, pin_defs_dict = minion_tools.config_gpio(defaults=True)

# Get the current time stamp information
samp_time = minion_tools.update_timestamp()  # Use when DS3231 is not enabled in config.txt

# Get the current sample number
samp_num = minion_tools.read_samp_num()

# Load the Minion Configuration
minion_mission_config = minion_tools.read_mission_config()

# Create an instance of MinionHat()
minion_hat = MinionHat()

# i = 0  # Not sure why this should be here.

IG_WIFI_Samples = (((minion_mission_config['IG_WIFI_D']*24) +
                    minion_mission_config['IG_WIFI_H'])/minion_mission_config['Srate']) - \
                  (minion_mission_config['INIsamp_hours']/minion_mission_config['Srate'])

print("Minion Deployment Handler")
print("Current Date/Time:  {}".format(samp_time))
# print("Days : {}".format(minion_mission_config['Ddays']))
print("Time-Lapse Mode Duration: {} hours".format(minion_mission_config['TLPsamp_hours']))
# print("Sample rate (hours) - {}".format(minion_mission_config['Srate']))
print("Time-Lapse Burst Sample Interval: {} minutes".format(minion_mission_config['TLPsamp_interval_minutes']))

# TotalSamples = ((minion_mission_config['Ddays'] * 24) + minion_mission_config['TLPsamp_hours']) / \
#                minion_mission_config['Srate']

# TotalSamples = minion_mission_config['TLPsamp_hours'] / minion_mission_config['Srate']
TotalSamples = (minion_mission_config['TLPsamp_hours'] * 60) / minion_mission_config['TLPsamp_interval_minutes']

if samp_num >= TotalSamples:
    RemainSamples = 0
else:
    RemainSamples = (TotalSamples - samp_num)

print("Total Cycles ------- {}".format(TotalSamples))

print("Cycles Remaining --- {}".format(RemainSamples))

if IG_WIFI_Samples >= samp_num:
    IgnoreWIFI = True
    print("Ignoring Wifi, in Mission")

else:
    IgnoreWIFI = False
    print("Searching for WIFI...")

ifswitch = "sudo python /home/pi/Documents/Minion_tools/dhcp-switch.py"

iwlist = 'sudo iwlist wlan0 scan | grep -e "Minion_Hub" -e "Master_Hub"'

net_cfg = "ls /etc/ | grep dhcp"

ping_hub = "ping 192.168.0.1 -c 1"

ping_google = "ping google.com -c 1"

ps_test = "pgrep -a python"

scriptNames = ["TempPres.py", "Minion_image.py", "Minion_image_IF.py", "OXYBASE_RS232.py", "Initial_Sampler.py",
               "Recovery_Sampler_Burn.py", "TempPres_IF.py", "OXYBASE_RS232_IF.py", "xmt_minion_data.py"]

# Flag to indicate that the time-lapse mode should start immediately after the Initial Sampler completes
start_time_lapse_scripts_flag = False

if __name__ == '__main__':

    # First, check for Wifi
    if minion_tools.check_wifi(IgnoreWIFI) == "Connected":
        minion_tools.kill_sampling(scriptNames)
        minion_tools.flash(2, 250, 250)
        GPIO.output(pin_defs_dict['LED_RED'], GPIO.HIGH)
        exit(0)

    # Initial Sampling Mode
    if samp_num == 0:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/Initial_Sampler.py &')
        start_time_lapse_scripts_flag = True

    # Recovery Sampling Mode
    # elif samp_num >= TotalSamples + 1 or minion_mission_config['Abort']:
    elif samp_num > TotalSamples or minion_mission_config['Abort']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/Recovery_Sampler_Burn.py &')
        shdn_seconds = 60

    # Time-Lapse Sampling Mode
    else:
        start_time_lapse_scripts()
        # Calculate Shutdown time for Time-Lapse Mode
        shdn_seconds = 60 * (minion_mission_config['TLPsamp_interval_minutes'] -
                             minion_mission_config['TLPsamp_burst_minutes'])

    # time.sleep(60)  # For testing only!!!

    # Increment the Sample Number
    minion_tools.increment_samp_num()
    
    check_wifi_and_scripts(scriptNames)

    if start_time_lapse_scripts_flag:
        start_time_lapse_scripts()
        minion_tools.increment_samp_num()
        # Calculate Shutdown time for Time-Lapse Mode
        shdn_seconds = 60 * (minion_mission_config['TLPsamp_interval_minutes'] -
                             minion_mission_config['TLPsamp_burst_minutes'])

    check_wifi_and_scripts(scriptNames)

    # Once we get here, there are none of the scripts in scriptNames are running.
    print('Goodbye')

    # Calculate the shutdown time
    minion_hat.shutdown(int(shdn_seconds))

    # time.sleep(5)
    # os.system('sudo shutdown now')
