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
        ig_wifi_status = minion_tools.ignore_wifi_check()
        if minion_tools.check_wifi(ig_wifi_status) == "Connected":
            minion_tools.kill_sampling(script_list)
            minion_tools.flash(2, 250, 250)
            GPIO.output(pin_defs_dict['LED_GRN'], GPIO.LOW)
            GPIO.output(pin_defs_dict['LED_RED'], GPIO.HIGH)
            exit(0)
        else:
            print("Sampling")
            time.sleep(5)


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

TotalSamples = (minion_mission_config['TLPsamp_hours'] * 60) / minion_mission_config['TLPsamp_interval_minutes']

if samp_num >= TotalSamples:
    RemainSamples = 0
else:
    RemainSamples = (TotalSamples - samp_num)

print("="*50)
print("Gelcam Deployment Handler")
print("Current Date/Time:  {}".format(samp_time))
print("Gelcam Mission Duration: {} hours".format(minion_mission_config['TLPsamp_hours']))
print("Gelcam Burst Sample Interval: {} minutes".format(minion_mission_config['TLPsamp_interval_minutes']))
print("Total Sample Bursts ------- {}".format(TotalSamples))
print("Sample Bursts Remaining --- {}".format(RemainSamples))
print("="*50)

ps_test = "pgrep -a python"

scriptNames = ["TempPres.py", "Minion_image.py", "OXYBASE_RS232.py"]

if __name__ == '__main__':

    # First, check for Wifi
    ignore_wifi_status = minion_tools.ignore_wifi_check()
    if minion_tools.check_wifi(ignore_wifi_status) == "Connected":
        minion_tools.kill_sampling(scriptNames)
        minion_tools.flash(3, 250, 250)
        GPIO.output(pin_defs_dict['LED_RED'], GPIO.HIGH)
        exit(0)

    if minion_mission_config['iniP30'] or minion_mission_config['iniP100'] or minion_mission_config['iniTmp']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/TempPres.py &')

    if minion_mission_config['iniImg']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/Minion_image.py --mode tlp &')

    if minion_mission_config['iniO2']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/OXYBASE_RS232.py &')

    check_wifi_and_scripts(scriptNames)

    # Once we get here, there are none of the scripts in scriptNames are running.
    print('Goodbye')

    # This is the mode between Time-Lapse Mode bursts
    # Calculate (roughly) Shutdown time for Time-Lapse Mode
    shutdown_seconds = 60 * (minion_mission_config['TLPsamp_interval_minutes'] -
                             minion_mission_config['TLPsamp_burst_minutes'])
    minion_hat.shutdown(int(shutdown_seconds))
