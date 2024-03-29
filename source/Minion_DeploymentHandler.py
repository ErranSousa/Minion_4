#!/usr/bin/env python3

import time
import os
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox
from minion_hat import MinionHat

# Constants
shutdown_delay_secs = 20  # The shutdown delay is programmable through the minion_hat
rpi_boot_time_secs = 38  # This needs to be refined, placeholder.  TODO: calculate rpi_boot_time on the fly


# def check_wifi_and_scripts(script_list):
#     time.sleep(5)  # Wait for things to settle before checking for wifi & scripts
#     # tic_3 = 0
#     # Check for WiFi while any of the scripts in script_list are executing
#     while any(x in os.popen(ps_test).read() for x in script_list):
#         ig_wifi_status = minion_tools.ignore_wifi_check()
#         if minion_tools.check_wifi(ig_wifi_status) == "Connected":
#             minion_tools.kill_sampling(script_list)
#             minion_tools.flash(2, 250, 250)
#             GPIO.output(pin_defs_dict['LED_GRN'], GPIO.LOW)
#             GPIO.output(pin_defs_dict['LED_RED'], GPIO.HIGH)
#             exit(0)
#         else:
#             print('[ ' + '\33[92mSampling\33[0m' + ' ]')
#             # Need to capture a tic here to account for the 5 sec when going into time-lapse
#             # directly from Initial Mode
#             # tic_3 = time.perf_counter()
#             time.sleep(5)
#     return time.perf_counter()

def check_wifi_and_scripts(script_list):
    time.sleep(5)  # Wait for things to settle before checking for wifi & scripts
    delta_secs = 0.1
    tm_total_secs = 3
    num_loops = tm_total_secs / delta_secs
    loop_count = num_loops
    # Check for WiFi while any of the scripts in script_list are executing
    while any(x in os.popen(ps_test).read() for x in script_list):
        if not loop_count:
            ig_wifi_status = minion_tools.ignore_wifi_check()
            if minion_tools.check_wifi(ig_wifi_status) == "Connected":
                minion_tools.kill_sampling(script_list)
                minion_tools.flash(2, 250, 250)
                GPIO.output(pin_defs_dict['LED_GRN'], GPIO.LOW)
                GPIO.output(pin_defs_dict['LED_RED'], GPIO.HIGH)
                exit(0)
            else:
                print('[ ' + '\33[92mSampling\33[0m' + ' ]')
            loop_count = num_loops
        time.sleep(delta_secs)
        loop_count -= 1
    return time.perf_counter()


def start_time_lapse_scripts():
    if minion_mission_config['iniImg']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/Minion_image.py --mode tlp &')

    if minion_mission_config['iniP30'] or minion_mission_config['iniP100'] or minion_mission_config['iniTmp']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/TempPres.py &')

    if minion_mission_config['iniO2']:
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/OXYBASE_RS232.py --mode TLP &')


# Start by grabbing the first time mark.  Used in calculating the total time of sampling, including any setup.
tic = time.perf_counter()

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
print("Minion Deployment Handler")
print("Current Date/Time:  {}".format(samp_time))
print("Time-Lapse Mode Duration: {} hours".format(minion_mission_config['TLPsamp_hours']))
print("Time-Lapse Burst Sample Interval: {} minutes".format(minion_mission_config['TLPsamp_interval_minutes']))
print("Total Sample Bursts ------- {}".format(TotalSamples))
print("Sample Bursts Remaining --- {}".format(RemainSamples))
print("="*50)

ps_test = "pgrep -a python"

# TODO: Review for dead script names
scriptNames = ["TempPres.py", "Minion_image.py", "OXYBASE_RS232.py", "Initial_Sampler.py",
               "Recovery_Sampler_Burn.py", "xmt_minion_data.py"]

# Flag to indicate that the time-lapse mode should start immediately after the Initial Sampler completes
start_time_lapse_scripts_flag = False
# Flag to indicate recovery mode
recovery_mode_flag = False

if __name__ == '__main__':

    while True:

        toc_1 = time.perf_counter()

        # Get the current sample number
        samp_num = minion_tools.read_samp_num()

        # First, check for Wifi
        ignore_wifi_status = minion_tools.ignore_wifi_check()
        if minion_tools.check_wifi(ignore_wifi_status) == "Connected":
            minion_tools.kill_sampling(scriptNames)
            minion_tools.flash(2, 250, 250)
            GPIO.output(pin_defs_dict['LED_RED'], GPIO.HIGH)
            exit(0)

        # Initial Sampling Mode
        if samp_num == 1:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/Initial_Sampler.py &')
            start_time_lapse_scripts_flag = True

        # Recovery Sampling Mode
        elif samp_num > TotalSamples + 1 or minion_mission_config['Abort']:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/Recovery_Sampler_Burn.py &')
            recovery_mode_flag = True

        # Time-Lapse Sampling Mode
        else:
            start_time_lapse_scripts()

        tic_2 = check_wifi_and_scripts(scriptNames)

        # Increment the Sample Number after scripts have completed
        minion_tools.increment_samp_num()

        # Start the Time-Lapse Mode Samples immediately after the Initial Samples - no shutdown
        if start_time_lapse_scripts_flag:
            tic = tic_2  # Need to reset the tic for accurate timing
            toc_1 = tic_2
            start_time_lapse_scripts()
            check_wifi_and_scripts(scriptNames)

        # check_wifi_and_scripts(scriptNames)  # Todo: consider moving this to inside the above if-statement

        # If the first Time-Lapse mode burst was performed, the sample number needs to be incremented
        if start_time_lapse_scripts_flag:
            minion_tools.increment_samp_num()
            start_time_lapse_scripts_flag = False

        # Once we get here, there are none of the scripts in scriptNames are running.
        print('Goodbye')

        # Between Time Lapse Mode Blocks, the system should enter the lowest power mode (shutdown).
        # Shutdown will disable the recovery strobe and burn wire to conserve power.
        # Once recovery mode is reached, the power down between cycles should preserve the
        # burn wire and recovery strobe (sleep).
        if not recovery_mode_flag:
            # This is the mode between Time-Lapse Mode bursts
            # Calculate (roughly) Shutdown time for Time-Lapse Mode
            toc = time.perf_counter()  # Capture the counter again
            total_sample_burst_secs = toc - tic
            shutdown_seconds = (minion_mission_config['TLPsamp_interval_minutes'] * 60 -
                                total_sample_burst_secs -
                                shutdown_delay_secs -
                                rpi_boot_time_secs)
            # if shutdown_seconds >= 120:
            tm_diff_secs = (minion_mission_config['TLPsamp_interval_minutes'] -
                            minion_mission_config['TLPsamp_burst_minutes']) * 60
            if tm_diff_secs >= 120:
                minion_hat.shutdown(int(shutdown_seconds))
            else:
                total_sample_burst_secs = time.perf_counter() - toc_1
                shutdown_seconds = (minion_mission_config['TLPsamp_interval_minutes'] * 60 - total_sample_burst_secs)
                if shutdown_seconds < 0:
                    shutdown_seconds = 0
                print('Sleeping for ' + str(shutdown_seconds) + ' seconds')
                time.sleep(shutdown_seconds)
        else:
            # This is the mode between Recovery sampler shutdowns where the burn wire and recovery strobe are preserved.
            toc = time.perf_counter()  # Capture the counter again
            total_final_mode_secs = toc - tic
            sleep_seconds = (minion_mission_config['gps_transmission_interval'] * 60 -
                             total_final_mode_secs -
                             shutdown_delay_secs -
                             rpi_boot_time_secs)

            # The intent here is to ensure that we get the gps_transmission_interval sleep time after sending data
            if sleep_seconds < 0:
                sleep_seconds = minion_mission_config['gps_transmission_interval'] * 60

            # Just system delay without shutting down if the sleep_seconds are within a defined range,
            # otherwise power down and sleep
            if 0 < sleep_seconds < 120:
                sleep_seconds = (minion_mission_config['gps_transmission_interval'] * 60 - total_final_mode_secs)
                time.sleep(sleep_seconds)
            else:
                minion_hat.sleep(int(sleep_seconds))
