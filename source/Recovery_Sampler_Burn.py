#!/usr/bin/env python3

import RPi.GPIO as GPIO
import tsys01
import ms5837
from kellerLD import KellerLD
import pickle
import time
import os
import math
import configparser
import sys
sys.path.insert(0,'/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

#Defines
DATA_TYPE = '$03'  # Final Sampling Type Data
MIN_DEPTH = 5  # Minimum Depth in dBar
MIN_DEPTH_CNTR_THRESHOLD = 5  # Number of minimum pressure measurements before triggering a minimum depth condition
ENABLE_MIN_DEPTH_CUTOUT = False  # Enables the Minimum Depth Cutout Feature
ENABLE_MIN_DEPTH_CUTOUT_TEST = False  # TEST MODE ONLY!!!  DO NOT DEPLOY SET TO TRUE!!!

# Pin Assignments
BURN = 33
DATA_REC_PIN = 16

# Initializations
samp_count = 1
NumSamples = 0
BURN_WIRE = False
min_depth_cntr = 0  # Count of the number of minimum depth measurements
min_depth_flag = False  # Flag to indicate that a minimum depth condition exists
if ENABLE_MIN_DEPTH_CUTOUT_TEST == True:
    min_depth_base_press = 17500


ps_test = "pgrep -a python"

# GPIO Initializations
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BURN, GPIO.OUT)
GPIO.output(BURN, 1)
GPIO.setup(DATA_REC_PIN, GPIO.OUT)
GPIO.output(DATA_REC_PIN, 1)

# pickle to hold True or False denoting if the Final Samples have been performed
fname_final_status_pickle = "/home/pi/Documents/Minion_scripts/final_samp_status.pkl"


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def abortMission(configLoc):

    abortConfig = configparser.ConfigParser()
    abortConfig.read(configLoc)
    abortConfig.set('Mission','Abort','1')
    with open(config,'wb') as abortFile:
        abortConfig.write(abortFile)


def kill_sampling(scriptNames):

    for script in scriptNames:
        os.system("sudo pkill -9 -f {}".format(script))


def read_sampcount():
    #countp = open("/home/pi/Documents/Minion_scripts/sampcount.pkl","rb")
    with open("/home/pi/Documents/Minion_scripts/sampcount.pkl","rb") as countp:
        sampcount = pickle.load(countp)
    #countp.close()
    return sampcount


def write_pickle_file(fname_pickle,data):
    #print("File Name: " + fname_pickle)
    #disp_data_xmt_status_dict(dict_to_write)
    #pickle_file_fid = open(fname_pickle,'wb')
    with open(fname_pickle,'wb') as pickle_file_fid:
        pickle.dump(data,pickle_file_fid)


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
    #try to open the Data Transmit Status pickle file
    try:
        #Try to open the pickle file.  If it exists, read the data out.
        with open(pickle_file_name,'rb') as pickle_file:
            print("\n\rFound pickle file: " + pickle_file_name)
            print("Loading " + pickle_file_name)
            final_samp_status_flag = pickle.load(pickle_file)
            print("Final Sample Status Flag: " + str(final_samp_status_flag))
        return final_samp_status_flag
    except:
        #Could not open the pickle file so it must be the first time through
        print("\n\rCould not find the pickle file.  Creating " + pickle_file_name)
        write_pickle_file(pickle_file_name,False)
        return False
    finally:
        #Now, close the pickle file.
        try:
            pickle_file.close()
            print("File Closed: " + pickle_file_name)
        except:
            pass


minion_tools = MinionToolbox()  # create an instance of MinionToolbox() called minion_tools

# Read out final samples status.
#    True = Final Samples Performed, False = Final Samples Not Performed
final_samp_status_flag = read_final_samp_status_pickle(fname_final_status_pickle)

scriptNames = ["TempPres.py", "Minion_image.py","Minion_image_IF.py","OXYBASE_RS232.py", \
               "ACC_100Hz.py","Initial_Sampler.py","TempPres_IF.py","OXYBASE_RS232_IF.py", \
               "ACC_100Hz_IF.py","Iridium_gps.py","Iridium_data.py","xmt_minion_data.py"]

if(any(x in os.popen(ps_test).read() for x in scriptNames)) == True:

    kill_sampling(scriptNames)

data_config = configparser.ConfigParser()
data_config.read('/home/pi/Documents/Minion_scripts/Data_config.ini')

configDir = data_config['Data_Dir']['Directory']
configLoc = '{}/Minion_config.ini'.format(configDir)
config = configparser.ConfigParser()
config.read(configLoc)
Abort = str2bool(config['Mission']['Abort'])
iniImg = str2bool(config['Sampling_scripts']['Image'])
iniP30 = str2bool(config['Sampling_scripts']['30Ba-Pres'])
iniP100 = str2bool(config['Sampling_scripts']['100Ba-Pres'])
iniTmp = str2bool(config['Sampling_scripts']['Temperature'])
iniO2  = str2bool(config['Sampling_scripts']['Oxybase'])
iniAcc = str2bool(config['Sampling_scripts']['ACC_100Hz'])

MAX_Depth = int(config['Mission']['MAX_Depth'])

Ddays = int(config['Deployment_Time']['days'])
Dhours = int(config['Deployment_Time']['hours'])

Srate = float(config['Sleep_cycle']['Minion_sleep_cycle'])

TotalCycles = int((((Ddays*24)+Dhours))/Srate)

samp_count = int(read_sampcount())

print("A--> Srate: " + str(Srate) + ", TotalCycles: " + str(TotalCycles) + \
      ", samp_count: " + str(samp_count))

with open("/home/pi/Documents/Minion_scripts/timesamp.pkl","rb") as firstp:
    samp_time = pickle.load(firstp)

samp_count_leading_zeros = "%03d" % samp_count

samp_time = "{}-{}".format(samp_count_leading_zeros, samp_time) #Add leading zeros to sample count

Stime = float(config['Final_Samples']['hours'])
Srate = float(config['Final_Samples']['TempPres_sample_rate'])

file_name = "{}_TEMPPRES-FIN.txt".format(samp_time)
file_path_name = "{}/minion_data/FIN/".format(configDir) + file_name

Sf = 1/Srate

TotalSamples = Stime*60*60*Srate

#print for testing only!
print("B--> Srate: " + str(Srate) + ", Stime: " + str(Stime) + ", TotalSamples: " + \
      str(TotalSamples))

######################

time.sleep(1)

if iniP30 == True:

    Psensor = ms5837.MS5837_30BA() # Default I2C bus is 1 (Raspberry Pi 3)

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

if iniP100 == True:

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

if iniTmp == True:

    sensor_temp = tsys01.TSYS01()

    # We must initialize the sensor before reading it
    if not sensor_temp.init():
        print("Error initializing Temperature sensor")
        exit(1)

if iniP100 == False and iniP30 == False:
    Pres_ini = 2000

if __name__ == '__main__':
    
    print("C--> samp_count: " + str(samp_count) + ", TotalCycles + 1: " + str(TotalCycles+1))
    
    if Pres_ini == "Broken":
        print("Pressure Sensor Not Working...")
        abortMission(configLoc)
        os.system('sudo python /home/pi/Documents/Minion_scripts/Iridium_gps.py')

#    if Abort == True:
#        GPIO.output(BURN,1)
#        os.system('sudo python /home/pi/Documents/Minion_scripts/Iridium_gps.py')

    if final_samp_status_flag == False:
        GPIO.output(BURN,1)
        #Create the final samples data file only if the final samples have not been performed
        minion_tools.write_data_file_header(DATA_TYPE,file_path_name,file_name,Srate,iniP30,iniP100,iniTmp)

        scriptNames2 = ["Minion_image_IF.py","OXYBASE_RS232_IF.py","ACC_100Hz_IF.py"]
        
        if iniImg == True:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/Minion_image_IF.py &')

        if iniO2 == True:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/OXYBASE_RS232_IF.py &')

        if iniAcc == True:
            os.system('sudo python3 /home/pi/Documents/Minion_scripts/ACC_100Hz_IF.py &')

        # Spew readings
        while(NumSamples <= TotalSamples and min_depth_flag == False):

            tic = time.perf_counter()
            
            #Indicate to the user in which mode the Minion is operating
            print("")
            print("Final Sampling Mode")
            print("Samples Remaining: " + str(TotalSamples - NumSamples))

            sensor_string = ''

            if iniP100 or iniP30 == True:

                if Psensor.read():
                    #shifting the decimal point out
                    Ppressure = round((Psensor.pressure() * depth_factor) - surface_offset, 3)*1000
                    Ppressure = "%07d" % Ppressure  #prepending zeros 
                    Ptemperature = round(Psensor.temperature(),2)*100
                    Ptemperature = "%04d" % Ptemperature
                    Pres_data = "{},{},".format(Ppressure, Ptemperature)
                    print("Pressure sensor data: {}".format(Pres_data))
                    sensor_string = "{}{}".format(sensor_string,Pres_data)

                else:
                    print('Pressure Sensor ded')
                    with open(file_path_name,"a") as file:
                        file.write('Pressure Sensor fail')
                    abortMission(configLoc)

                if int(Ppressure)/1000 >= MAX_Depth:
                    with open(file_path_name,"a") as file:
                        file.write("Minion Exceeded Depth Maximum!")
                    abortMission(configLoc)


            if iniTmp == True:

                if not sensor_temp.read():
                    print("Error reading sensor")
                    iniTmp = False

                Temp_acc = round(sensor_temp.temperature(),2)*100
                Temp_acc = "%04d" % Temp_acc

                print("Temperature_accurate: {} C*100".format(Temp_acc)) #degrees Celsius * 100

                sensor_string = '{}{}'.format(sensor_string, Temp_acc)

            with open(file_path_name,"a") as file:
                file.write("\n{}".format(sensor_string))  

            NumSamples = NumSamples + 1

            toc = time.perf_counter()

            timeS = toc - tic

            if timeS >= Sf:

                timeS = Sf

            time.sleep(Sf - timeS)

            #Minimum Depth Cutout Feature
            if iniP100 or iniP30 == True:
                if ENABLE_MIN_DEPTH_CUTOUT == True:
                    if ENABLE_MIN_DEPTH_CUTOUT_TEST == True:
                        min_depth_base_press -= 500 #decrement by 500
                        if min_depth_base_press < 0:
                            min_depth_base_press = 0  #Don't let it go negative
                        Ppressure = min_depth_base_press
                    if int(Ppressure)/1000 <= MIN_DEPTH:
                        min_depth_cntr += 1
                        print("\nMinimum Depth Count: " + str(min_depth_cntr) + ", Pressure: " + str(int(Ppressure)/1000))
                    if min_depth_cntr >= MIN_DEPTH_CNTR_THRESHOLD:
                        if(any(x in os.popen(ps_test).read() for x in scriptNames2)) == True:
                            kill_sampling(scriptNames)
                        print("Minimum Depth Condition Detected.")
                        print("Ending Sampling and preparing to transmit data.")
                        write_pickle_file(fname_final_status_pickle,True)
                        min_depth_flag = True
                        GPIO.output(DATA_REC_PIN, 0)  #Turn off the DATA Receive LED Inidicator
                        os.system('sudo python /home/pi/Documents/Minion_scripts/xmt_minion_data.py &')

        #At this point, all final Pressure & Temperature samples have completed
        #Need to end sampling of other sensors as well
        if(any(x in os.popen(ps_test).read() for x in scriptNames2)) == True:
            kill_sampling(scriptNames)
        write_pickle_file(fname_final_status_pickle,True) 
        GPIO.output(DATA_REC_PIN, 0)  #Turn off the DATA Receive LED Inidicator


    else:
        GPIO.output(BURN,1)
        os.system('sudo python /home/pi/Documents/Minion_scripts/xmt_minion_data.py &')

    time.sleep(60)
