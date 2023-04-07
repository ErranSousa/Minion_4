#!/usr/bin/env python3

# import RPi.GPIO as GPIO
import tsys01
import ms5837
from kellerLD import KellerLD
import pickle
import time
import os
# import math
import configparser
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox
from minion_hat import MinionHat

# Defines
DATA_TYPE = '$03'  # Final Sampling Type Data
MIN_DEPTH = 5  # Minimum Depth in dBar
MIN_DEPTH_CNTR_THRESHOLD = 5  # Number of minimum pressure measurements before triggering a minimum depth condition
ENABLE_MIN_DEPTH_CUTOUT = False  # Enables the Minimum Depth Cutout Feature
ENABLE_MIN_DEPTH_CUTOUT_TEST = False  # TEST MODE ONLY!!!  DO NOT DEPLOY SET TO TRUE!!!

# Initializations
samp_num = 1
NumSamples = 0
min_depth_cntr = 0  # Count of the number of minimum depth measurements
min_depth_flag = False  # Flag to indicate that a minimum depth condition exists
if ENABLE_MIN_DEPTH_CUTOUT_TEST:
    min_depth_base_press = 17500

# pickle to hold True or False denoting if the Final Samples have been performed
fname_final_status_pickle = "/home/pi/Documents/Minion_scripts/final_samp_status.pkl"

ps_test = "pgrep -a python"

# create an instance of MinionToolbox()
minion_tools = MinionToolbox()

# Create an instance of MinionHat()
minion_hat = MinionHat()

# Configure the Raspberry Pi GPIOs
GPIO, pin_defs_dict = minion_tools.config_gpio()

# Load the Minion Configuration
minion_mission_config = minion_tools.read_mission_config()

# Load the Data Configuration Directory
data_config = minion_tools.read_data_config()

# Minion Mission Configuration file
configLoc = '{}/Minion_config.ini'.format(data_config['Data_Dir'])

# Get the current sample number
samp_num = minion_tools.read_samp_num()

# Get the current time stamp information
samp_time = minion_tools.read_timestamp()  # Use when DS3231 is not enabled in config.txt

# Enable the burn wire
minion_hat.burn_wire(minion_hat.ENABLE)

# Enable the Recovery Strobe
minion_hat.strobe(minion_hat.ENABLE)

# Indicate that data is being collected
GPIO.output(pin_defs_dict['LED_GRN'], GPIO.HIGH)

# Temporary Setting for Testing Only
minion_hat.strobe_timing(500, 500)  # On for .5 Seconds / Off for .5 seconds

def abortMission(configLoc):

    abortConfig = configparser.ConfigParser()
    abortConfig.read(configLoc)
    abortConfig.set('Mission', 'Abort', '1')
    with open(config, 'wb') as abortFile:
        abortConfig.write(abortFile)


def write_pickle_file(fname_pickle, data):
    with open(fname_pickle, 'wb') as pickle_file_fid:
        pickle.dump(data, pickle_file_fid)


def read_final_samp_status_pickle(fname_final_status_pickle):
    """Reads the Final Sampling Status Flag.
    The state stored in the piclke file will be True if the
    Final Sampling completed and False if not.

    Parameters
    ----------
    fname_final_status_pickle : 'string' Name of pickle file

    Returns:
    --------
    final_samp_status_flag : 'True' or 'False' State of the Final Sampling Status
    """
    pickle_file_name = fname_final_status_pickle
    # try to open the Data Transmit Status pickle file
    try:
        # Try to open the pickle file.  If it exists, read the data out.
        with open(pickle_file_name, 'rb') as pickle_file:
            print("\n\rFound pickle file: " + pickle_file_name)
            print("Loading " + pickle_file_name)
            final_samp_status_flag = pickle.load(pickle_file)
            print("Final Sample Status Flag: " + str(final_samp_status_flag))
        return final_samp_status_flag
    except:
        # Could not open the pickle file so it must be the first time through
        print("\n\rCould not find the pickle file.  Creating " + pickle_file_name)
        write_pickle_file(pickle_file_name, False)
        return False
    finally:
        # Now, close the pickle file.
        try:
            pickle_file.close()
            print("File Closed: " + pickle_file_name)
        except:
            pass


# Read out final samples status.
# True = Final Samples Performed, False = Final Samples Not Performed
final_samp_status_flag = read_final_samp_status_pickle(fname_final_status_pickle)

# scriptNames = ["TempPres.py", "Minion_image.py", "Minion_image_IF.py", "OXYBASE_RS232.py",
#                "ACC_100Hz.py", "Initial_Sampler.py", "TempPres_IF.py", "OXYBASE_RS232_IF.py",
#                "ACC_100Hz_IF.py", "Iridium_gps.py", "Iridium_data.py", "xmt_minion_data.py"]

scriptNames = ["TempPres.py", "Minion_image.py", "Minion_image_IF.py", "OXYBASE_RS232.py",
               "Initial_Sampler.py", "TempPres_IF.py", "OXYBASE_RS232_IF.py",
               "Iridium_gps.py", "Iridium_data.py", "xmt_minion_data.py"]

if any(x in os.popen(ps_test).read() for x in scriptNames):
    minion_tools.kill_sampling(scriptNames)

TotalSamples = ((minion_mission_config['Ddays'] * 24) + minion_mission_config['Dhours']) / minion_mission_config['Srate']

print("A--> Srate: " + str(minion_mission_config['Srate']) + ", TotalCycles: " + str(TotalSamples) +
      ", samp_num: " + str(samp_num))

print('Timestamp: {}'.format(samp_time))
# with open("/home/pi/Documents/Minion_scripts/timesamp.pkl","rb") as firstp:
#     samp_time = pickle.load(firstp)

samp_num_leading_zeros = "%03d" % samp_num

samp_time = "{}-{}".format(samp_num_leading_zeros, samp_time)  # Add leading zeros to sample count

file_name = "{}_TEMPPRES-FIN.txt".format(samp_time)
file_path_name = "{}/minion_data/FIN/".format(data_config['Data_Dir']) + file_name

Sf = 1/minion_mission_config['FINsamp_tempPres_rate']

TotalSamples = minion_mission_config['FINsamp_hours']*60*60*minion_mission_config['FINsamp_tempPres_rate']

#print for testing only!
print("B--> Final Samples Press/Temp rate: " + str(minion_mission_config['FINsamp_tempPres_rate']) + ", Final Sample Hours: " +
      str(minion_mission_config['FINsamp_hours']) + ", TotalSamples: " + str(TotalSamples))

######################

time.sleep(1)

if minion_mission_config['iniP30']:

    Psensor = ms5837.MS5837_30BA()  # Default I2C bus is 1 (Raspberry Pi 3)

    if not Psensor.init():
        print("Failed to initialize P30 sensor!")
        exit(1)

    depth_factor = .01
    surface_offset = 10

    # We have to read values from sensor to update pressure and temperature
    if Psensor.read():
        Pres_ini = round((Psensor.pressure() * depth_factor) - surface_offset, 3)
    else:
        Pres_ini = "Broken"

if minion_mission_config['iniP100']:

    Psensor = KellerLD()

    if not Psensor.init():
        print("Failed to initialize P100 sensor!")
        exit(1)

    depth_factor = 10
    surface_offset = 0

    # We have to read values from sensor to update pressure and temperature
    if Psensor.read():
        Pres_ini = round((Psensor.pressure() * depth_factor) - surface_offset, 3)
    else:
        Pres_ini = "Broken"

if minion_mission_config['iniTmp']:

    sensor_temp = tsys01.TSYS01()

    # We must initialize the sensor before reading it
    if not sensor_temp.init():
        print("Error initializing Temperature sensor")
        exit(1)

if not minion_mission_config['iniP100'] and not minion_mission_config['iniP30']:
    Pres_ini = 2000

if __name__ == '__main__':
    
    print("C--> samp_num: " + str(samp_num) + ", TotalSamples + 1: " + str(TotalSamples + 1))
    
    if Pres_ini == "Broken":
        print("Pressure Sensor Not Working...")
        abortMission(configLoc)
        os.system('sudo python /home/pi/Documents/Minion_scripts/Iridium_gps.py')

    if not final_samp_status_flag:
        minion_hat.burn_wire(minion_hat.ENABLE)
        # Create the final samples' data file only if the final samples have not been performed
        # Write a header to the data file
        minion_tools.write_data_file_header(DATA_TYPE, file_path_name, file_name,
                                            minion_mission_config['FINsamp_tempPres_rate'],
                                            minion_mission_config['iniP30'], minion_mission_config['iniP100'],
                                            minion_mission_config['iniTmp'])

        scriptNames2 = ["Minion_image_IF.py", "OXYBASE_RS232_IF.py"]

        if minion_mission_config['iniImg']:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/Minion_image_IF.py &')

        if minion_mission_config['iniO2']:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/OXYBASE_RS232_IF.py &')

        # if minion_mission_config['iniAcc']:
        #     os.system('sudo python3 /home/pi/Documents/Minion_scripts/ACC_100Hz_IF.py &')

        # Display readings
        while NumSamples <= TotalSamples and not min_depth_flag:

            tic = time.perf_counter()
            
            # Indicate to the user in which mode the Minion is operating
            print("")
            print("Final Sampling Mode")
            print("Samples Remaining: " + str(TotalSamples - NumSamples))

            sensor_string = ''

            if minion_mission_config['iniP100'] or minion_mission_config['iniP30']:

                if Psensor.read():
                    # shifting the decimal point out
                    Ppressure = round((Psensor.pressure() * depth_factor) - surface_offset, 3)*1000
                    Ppressure = "%07d" % Ppressure  # prepending zeros
                    Ptemperature = round(Psensor.temperature(), 2)*100
                    Ptemperature = "%04d" % Ptemperature
                    Pres_data = "{},{},".format(Ppressure, Ptemperature)
                    print("Pressure sensor data: {}".format(Pres_data))
                    sensor_string = "{}{}".format(sensor_string, Pres_data)

                else:
                    print('Pressure Sensor ded')
                    with open(file_path_name, "a") as file:
                        file.write('Pressure Sensor fail')
                    abortMission(configLoc)

                if int(Ppressure)/1000 >= minion_mission_config['MAX_Depth']:
                    with open(file_path_name, "a") as file:
                        file.write("Minion Exceeded Depth Maximum!")
                    abortMission(configLoc)

            if minion_mission_config['iniTmp']:

                if not sensor_temp.read():
                    print("Error reading sensor")
                    minion_mission_config['iniTmp'] = False

                Temp_acc = round(sensor_temp.temperature(), 2)*100
                Temp_acc = "%04d" % Temp_acc

                print("Temperature_accurate: {} C*100".format(Temp_acc))  # degrees Celsius * 100

                sensor_string = '{}{}'.format(sensor_string, Temp_acc)

            with open(file_path_name, "a") as file:
                file.write("\n{}".format(sensor_string))  

            NumSamples = NumSamples + 1

            toc = time.perf_counter()

            timeS = toc - tic

            if timeS >= Sf:

                timeS = Sf

            time.sleep(Sf - timeS)

            # Minimum Depth Cutout Feature
            if minion_mission_config['iniP100'] or minion_mission_config['iniP30']:
                if ENABLE_MIN_DEPTH_CUTOUT:
                    if ENABLE_MIN_DEPTH_CUTOUT_TEST:
                        min_depth_base_press -= 500  # decrement by 500
                        if min_depth_base_press < 0:
                            min_depth_base_press = 0  # Don't let it go negative
                        Ppressure = min_depth_base_press
                    if int(Ppressure)/1000 <= MIN_DEPTH:
                        min_depth_cntr += 1
                        print("\nMinimum Depth Count: " + str(min_depth_cntr) + ", Pressure: " + str(int(Ppressure)/1000))
                    if min_depth_cntr >= MIN_DEPTH_CNTR_THRESHOLD:
                        if any(x in os.popen(ps_test).read() for x in scriptNames2):
                            minion_tools.kill_sampling(scriptNames)
                        print("Minimum Depth Condition Detected.")
                        print("Ending Sampling and preparing to transmit data.")
                        write_pickle_file(fname_final_status_pickle, True)
                        min_depth_flag = True
                        GPIO.output(pin_defs_dict['LED_GRN'], GPIO.LOW)  # Turn off the DATA ACQ LED Inidicator
                        os.system('sudo python /home/pi/Documents/Minion_scripts/xmt_minion_data.py &')

        # At this point, all final Pressure & Temperature samples have completed
        # Need to end sampling of other sensors as well
        if any(x in os.popen(ps_test).read() for x in scriptNames2):
            minion_tools.kill_sampling(scriptNames)
        write_pickle_file(fname_final_status_pickle, True)
        GPIO.output(pin_defs_dict['LED_GRN'], GPIO.LOW)  # Turn off the DATA ACQ LED Inidicator

    else:
        print("Final Sampling Stage is complete.")
        minion_hat.burn_wire(minion_hat.ENABLE)
        os.system('sudo python /home/pi/Documents/Minion_scripts/xmt_minion_data.py &')

    time.sleep(10)
