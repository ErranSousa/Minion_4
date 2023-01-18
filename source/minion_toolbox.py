#!/usr/bin/env python3

"""! @brief API Set for Commonly Used Functionality in the Minion

"""
from __future__ import division  # Ensures Python3 division rules
import configparser
import os
import sys
import pickle
import RPi.GPIO as GPIO
import time
import datetime
from ds3231 import DS3231


# Pin Definitions
light = 12


data_config_file = '/home/pi/Documents/Minion_scripts/Data_config.ini'
pin_defs_file = '/home/pi/Documents/Minion_scripts/pin_defs.ini'
data_xmt_status_pickle_file = '/home/pi/Documents/Minion_scripts/data_xmt_status.pickle'
samp_num_pickle_file = '/home/pi/Documents/Minion_scripts/samp_num.pkl'
time_stamp_pickle_file = '/home/pi/Documents/Minion_scripts/timesamp.pkl'

# Command Aliases for Wifi
ifswitch = "sudo python /home/pi/Documents/Minion_tools/dhcp-switch.py"
iwlist = 'sudo iwlist wlan0 scan | grep -e "Minion_Hub" -e "Master_Hub"'
net_cfg = "ls /etc/ | grep dhcp"

class MinionToolbox(object):

    def __init__(self):
        self._py_ver_major = sys.version_info.major
        self._rtc_ext = DS3231()

    # str2bool will be depricated!!!  Use ans2bool()
    def str2bool(self,v):
        """Convert a string to a boolean"""
        return v.lower() in ("Y", "y", "yes", "true", "t", "1")


    def abort_mission(self):

        # Read the Minion Config File Location
        data_config = self.read_data_config()
        config_file = '{}/Minion_config.ini'.format(data_config['Data_Dir'])

        # Read / Load the Minion Config File
        config = configparser.ConfigParser()
        config.read(config_file)

        # Set the Abort field in Minion Config
        config.set('Mission', 'Abort', '1')

        # Save the changes to the Minion Config File
        with open(config_file, 'wb') as configFile:
            config.write(configFile)

        # What is all of this doing???
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(29, GPIO.OUT)
        GPIO.output(29, 0)
        os.system('sudo python3 /home/pi/Documents/Minion_scripts/Recovery_Sampler_Burn.py &')
        exit(0)


    def ans2bool(self,ans2convert):
        """Convert a yes/no or true/false answer to a boolean

        Answers that will result in a boolean 'True':
            "Y", "y", "yes", "true", "t", "1"

        Parameters
        ----------
        string ans2convert : Answer to convert

        Returns:
        --------
        boolean result : boolean of Answer

        Example:

            result = ans2bool("Y")
            print(result)

        """
        result = ans2convert.lower() in ("Y", "y", "yes", "true", "t", "1")
        return result

    def check_wifi(self,IgnoreStatus):
        """Checks for a Minion Hub and connects
           

        Parameters
        ----------
        bool IgnoreStatus : Connect to Minion Hub (True), Do not connect to Minion Hub (False)

        Returns:
        --------
        string status : Connection Status - "Connected" or "Not Connected"

           
        """

        # Prerequisites:  ifswitch, iwlist, net_cfg are defined
        networks = os.popen(iwlist).read()

        if "Master_Hub" in networks:
            print("Bypassing WIFI Lock")
            status = "Connected"

        elif "Minion_Hub" in networks and IgnoreStatus == False:
            status = "Connected"

        else:
            print("No WIFI found.")
            status = "Not Connected"

        if status == "Connected":
            net_status = os.popen(net_cfg).read()
            if ".Minion" in net_status:
                os.system(ifswitch)
            else:
                print("You have Minions!")

        print(status)
        return status

    def read_data_config(self):
        """Read the Minion Data Configuration Directory File

        Parameters
        ----------
        none

        Returns:
        --------
        dict data_config : Data Configuration Directory

        Example:
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_data_config_dict = minion_tools.read_data_config()
        """

        keys = ['Data_Dir']

        data_config = dict.fromkeys(keys)

        config = configparser.ConfigParser()
        config.read(data_config_file)

        data_config['Data_Dir'] = config['Data_Dir']['Directory']

        print('Data Config: ' + data_config['Data_Dir'])
        return data_config

    def read_mission_config(self):
        """Read the Minion Mission Configuration File

        Parameters
        ----------
        none

        Returns:
        --------
        dict mission_config : Minion Mission Configuration Dictionary
            keys:
                str Minion_ID : Minion Serial Number
                bool Abort : Enable / Disable Mission Abort Feature
                float MAX_Depth : Maximum Depth Limit in meters
                float IG_WIFI_D : Ignore WIFI Days
                float IG_WIFI_H : Ingnore WIFI Hours
                float INIsamp_hours : Number Sampling Hours (Initial Mode)
                float INIsamp_camera_rate : Camera Sample Rate (Initial Mode)
                float INIsamp_tempPres_rate : Temperature/Pressure Sample Rate (Initial Mode)
                float INIsamp_oxygen_rate : Oxygen Sample Rate (Initial Mode)
                float FINsamp_hours : Number Sampling Hours (Final Mode)
                float FINsamp_camera_rate : Camera Sample Rate (Finall Mode)
                float FINsamp_tempPres_rate : Temperature/Pressure Sample Rate (Final Mode)
                float FINsamp_oxygen_rate : Oxygen Sample Rate (Final Mode)
                int Ddays : Number of Deployment Days
                int Dhours : Number of Deployment Hours
                float Srate : Sleep Cycle
                float Stime : Sample Time
                float TLPsamp_minion_rate : Minion Sample Rate (Time-Lapse Mode)
                float TLPsamp_oxygen_rate : Oxygen Sample Rate (Time-Lapse Mode)
                bool iniImg : Enable / Disable Image Capture
                bool iniP30 : Enable / Disable 30 Bar Pressure Sensor
                bool iniP100 : Enable / Disable 100 Bar Pressure Sensor
                bool iniTmp : Enable/Disable Temperature Sensor
                bool iniO2 : Enable/Disable Oxygen Sensor
                bool iniAcc : Enable/Disable Accelerometer


        """

        #list of keys
        keys = ['Minion_ID','Abort','MAX_Depth','IG_WIFI_D','IG_WIFI_H',\
                'INIsamp_hours','INIsamp_camera_rate','INIsamp_tempPres_rate',\
                'INIsamp_oxygen_rate','FINsamp_hours','FINsamp_camera_rate',\
                'FINsamp_tempPres_rate','FINsamp_oxygen_rate','TLPsamp_minion_rate',\
                'TLPsamp_oxygen_rate','Ddays','Dhours','Stime','Srate','iniImg',\
                'iniP30','iniP100','iniTmp','iniO2','iniAcc'\
                ]

        mission_config = dict.fromkeys(keys)

        data_config = self.read_data_config()
        config_file = '{}/Minion_config.ini'.format(data_config['Data_Dir'])
        print('Mission Config: ' + config_file)

        config = configparser.ConfigParser()
        config.read(config_file)

        mission_config['Minion_ID'] = str(config['MINION']['Number'])

        mission_config['Abort'] = self.str2bool(config['Mission']['Abort'])
        mission_config['MAX_Depth'] = float(config['Mission']['Max_Depth'])
        mission_config['IG_WIFI_D'] = float(config['Mission']['Ignore_WIFI-days'])
        mission_config['IG_WIFI_H'] = float(config['Mission']['Ignore_WIFI-hours'])

        mission_config['INIsamp_hours'] = float(config['Initial_Samples']['hours'])
        mission_config['INIsamp_camera_rate'] = float(config['Initial_Samples']['Camera_sample_rate'])
        mission_config['INIsamp_tempPres_rate'] = float(config['Initial_Samples']['TempPres_sample_rate'])
        mission_config['INIsamp_oxygen_rate'] = float(config['Initial_Samples']['Oxygen_sample_rate'])

        mission_config['FINsamp_hours'] = float(config['Final_Samples']['hours'])
        mission_config['FINsamp_camera_rate'] = float(config['Final_Samples']['Camera_sample_rate'])
        mission_config['FINsamp_tempPres_rate'] = float(config['Final_Samples']['TempPres_sample_rate'])
        mission_config['FINsamp_oxygen_rate'] = float(config['Final_Samples']['Oxygen_sample_rate'])

        mission_config['Ddays'] = int(config['Deployment_Time']['days'])
        mission_config['Dhours'] = int(config['Deployment_Time']['hours'])

        mission_config['Srate'] = float(config['Sleep_cycle']['Minion_sleep_cycle'])

        Stime = config['Data_Sample']['Minion_sample_time']
        #Determine if the value entered into 'Minion_sample_time' is
        #    'Camera' or an actual number.
        #Note: Any text will work, not just 'Camera'
        try:
            mission_config['Stime'] = float(Stime)
        except:
            #Since Stime cannot be cast as a float, there must be some text
            #in the field such as 'Camera'
            mission_config['Stime'] = float(.2)
        mission_config['TLPsamp_minion_rate'] = float(config['Data_Sample']['Minion_sample_rate'])
        mission_config['TLPsamp_oxygen_rate'] = float(config['Data_Sample']['Oxygen_sample_rate'])

        mission_config['iniImg'] = self.str2bool(config['Sampling_scripts']['Image'])
        mission_config['iniP30'] = self.str2bool(config['Sampling_scripts']['30Ba-Pres'])
        mission_config['iniP100'] = self.str2bool(config['Sampling_scripts']['100Ba-Pres'])
        mission_config['iniTmp'] = self.str2bool(config['Sampling_scripts']['Temperature'])
        mission_config['iniO2']  = self.str2bool(config['Sampling_scripts']['Oxybase'])
        mission_config['iniAcc'] = self.str2bool(config['Sampling_scripts']['ACC_100Hz'])

        return mission_config

    def read_pin_defs(self):
        """Read the Minion Data Configuration Directory File

        Parameters
        ----------
        none

        Returns:
        --------
        dict pin_defs_dict : Minion Pin Definitions Dictionary
            keys:
                int SAMPLE_LED_RING : Sample LED Ring
                int BURN : Burn Wire Control
                int IO328 : I/O Line to ATMEGA328

        Example:
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            pin_defs_dict = minion_tools.read_pin_defs()
        """

        keys = ['SAMPLE_LED_RING', 'BURN', 'IO328']

        pin_defs_dict = dict.fromkeys(keys)

        config = configparser.ConfigParser()
        config.read(pin_defs_file)

        pin_defs_dict['SAMPLE_LED_RING'] = int(config['pin_defs']['SAMPLE_LED_RING'])
        pin_defs_dict['BURN'] = int(config['pin_defs']['BURN'])
        pin_defs_dict['IO328'] = int(config['pin_defs']['IO328'])

        return pin_defs_dict

    def update_timestamp(self):
        """Updates the timesamp piclke file

        Parameters
        ----------
        none

        Returns:
        --------
        str time_stamp : Formatted string containing the sample time stamp
                         Returns "9999-99-99_99-99-99" if an error occurred

        Example:
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            time_stamp = minion_tools.update_timestamp()
        """
        time_stamp = "9999-99-99_99-99-99"  # default time_stamp string
        try:
            # Get the Date and Time from the DS3231
            tm_now_dict = self.rtc_ext_get_time()

            # Compose the time_stamp string
            time_stamp = tm_now_dict['YYYY'] + "-" + tm_now_dict['MM'] + "-" + tm_now_dict['DD'] + "_" + tm_now_dict['hh'] + "-" + tm_now_dict['mm'] + "-" + tm_now_dict['ss']

            # Write the new time stamp to the pickle file
            with open("/home/pi/Documents/Minion_scripts/timesamp.pkl", "wb") as tm_stamp_pkl:
                pickle.dump(time_stamp, tm_stamp_pkl)

        except:
            print("Update time failed.")
            print("Hint: Super User Permission Required for accessing the time stamp pickle.")
        return time_stamp

    def read_timestamp(self):
        """Reads the timesamp pickle file

        Parameters
        ----------
        none

        Returns:
        --------
        str time_stamp : Formatted string containing the sample time stamp
                         Returns "9999-99-99_99-99-99" if an error occurred

        Example:
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            time_stamp = minion_tools.read_timestamp()
        """
        time_stamp = "9999-99-99_99-99-99"  # default time_stamp string

        with open(time_stamp_pickle_file, "rb") as tm_stamp_pkl:
            time_stamp = pickle.load(tm_stamp_pkl)

        return time_stamp


    def delete_data_xmt_status_pickle(self):
        """Delete the Data Transmit Status Pickle File

        Parameters
        ----------
        none

        Returns:
        --------
        none

        Example:
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.delete_data_xmt_status_pickle()
        """

        if os.path.exists(data_xmt_status_pickle_file):
            os.remove(data_xmt_status_pickle_file)
            print('[OK] Data Transmit Status Pickle File Removed.')
        else:
            print("[OK] Data Transmit Status Pickle File Already Removed or Does Not Exist.")

    def flash(self,num_flashes, ton, toff):
        """Flash the sampling LED Ring

        Parameters
        ----------
        num_flashes : number of flashes
        ton : Flash on time in milliseconds
        toff : Flash off time milliseconds

        Returns:
        --------
        none

        Example: Generate 2 flashes, 250ms on time, 250ms off time
        
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.strobe(2,250,250)

        Example: Simply illuminates the LED Ring for 2 seconds

            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.strobe(1,2000,0)

        Example: Dimmable Setting

            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.strobe(100,5,5)#Dim by 50%
        
        """
        #Setup the pin - eventually move this to its own method
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(light, GPIO.OUT)

        for val in range(num_flashes):
            GPIO.output(light, 1)
            time.sleep(ton/1000)
            # If we have done the requisite number of flashes,
            # no need for the final off time.
            if val == num_flashes - 1:
                break
            GPIO.output(light, 0)
            time.sleep(toff/1000)

        #Finally, turn off the LED Ring
        GPIO.output(light, 0)

    def kill_sampling(self,scriptNames):
        """Ends the python processes listed in scriptNames

        Parameters
        ----------
        list scriptNames : List of python scripts to kill

        Returns:
        --------
        none

        Example:
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            scriptNames = ["TempPres.py", "Minion_image.py"]
            minion_tools.kill_sampling(scriptNames)
         
        """
        for script in scriptNames:
            os.system("sudo pkill -9 -f {}".format(script))

    def write_data_file_header(self,data_type,file_path_name,file_name,samp_rate,iniP30,iniP100,iniTmp):
        """Write Header Record to Pressure & Temperature Data File

        Parameters
        ----------
        data_type : Data Type - INI:$02, TML:$03, FIN:$04
        file_path_name : Full path and name of the data file
        file_name : Name of data file
        samp_rate : Sample Rate
        iniP30 : Sensor Enabled - 30Bar Pressure Sensor
        iniP100 : Sensor Enabled - 100Bar Pressure Sensor
        iniTmp : Sensor Enabled - Temperature Sensor

        Returns:
        --------
        none
         
        """

        with open(file_path_name,"a+") as file:

            file.write(data_type) #Write Data Type Identifier
            file.write("," + file_name)  #Write the file name
            file.write("," + str(samp_rate))  #Write the sample rate

            if iniP30 == True:
                #file.write("Pressure(dbar),Temp(C)")
                file.write(",Pressure(dbar*1000),Temp(C*100)")  #Meta-Record for fixed field Press and Temp

            if iniP100 == True:
                #file.write("Pressure(dbar),Temp(C)")
                file.write(",Pressure(dbar*1000),Temp(C*100)")  #Meta-Record for fixed field Press and Temp

            if iniTmp == True:
                #file.write(", TempTSYS01(C)")
                file.write(",TempTSYS01(C*100)")

    def rtc_ext_get_time(self):
        """Read the Date and Time from the DS3231 External RTC

        Parameters
        ----------
        none

        Returns:
        --------
        dict the_time : Date and Time Dictionary
            keys:
                str YYYY : Year
                str MM : Month
                str DD : Day
                str hh : Hours
                str mm : Minutes
                str ss : Seconds
        """
        # print("Current Time:")
        return self._rtc_ext.read_time()

    def rtc_ext_disp_time(self, **kwargs):
        """Read and Display the Date and Time from the DS3231 External RTC

        Keyword Args:
        -------------
        verbose : displays the Date and Time (default True)

        Returns:
        --------
        str time_str : Date and Time String in the format YYYY/MM/DD hh:mm:ss
            where:
                str YYYY : Year
                str MM : Month
                str DD : Day
                str hh : Hours
                str mm : Minutes
                str ss : Seconds

        Additional Notes:
        -----------------
        This method can display the date and time but the user can also
        suppress this feature and simply use the returned string in their
        desired formatting.
        """
        options = {
            'verbose': True
        }
        options.update(kwargs)

        time_str = self._rtc_ext.disp_time(verbose=options['verbose'])

        return time_str

    def rtc_ext_set_time(self, **kwargs):
        """Set Date and Time on the DS3231 External RTC

        Keyword Args:
        -------------
        sync : synchronize the RPi Time to the DS3231 (default True)

        Returns:
        --------
        none

        Additional Notes:
        -----------------
        This method prompts the user to enter a new date and time.
        Enter a date in time several seconds in the future and then
        press 'enter' once the seconds are matched to a master clock.
        This method can also be used to check the time without
        changing the time by pressing 'enter' with no input at the prompt.
        By default, this method will also synchronize the RPi clock to
        the DS3231.  This may be disabled by setting the keyword argument
        sync = False.

        Example:  Set the external RTC and synchronize the RPi clock to it
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.rtc_ext_set_time()

        Example:  Set the external RTC only
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.rtc_ext_set_time(sync=False)

        """

        options = {
            'sync': True
        }
        options.update(kwargs)

        # Display the Current Date and Time on the External RTC
        now_time = self.rtc_ext_disp_time(verbose=False)
        print("\r\nDS3231 Current date and time [" + now_time + "]")

        # Prompt User to enter a new time
        if self._py_ver_major == 3:  # Python 3
            new_time = input("Enter a new date and time (YYYY/MM/DD hh:mm:ss): ")
        if self._py_ver_major == 2:  # Python 2
            new_time = raw_input("Enter a new date and time (YYYY/MM/DD hh:mm:ss): ")

        # Set the New Time
        success = self._rtc_ext.set_time(new_time)

        # Synchronize the RPi Time to the DS3231 RTC
        if options['sync'] == True and success == True:
            print("Synchronizing Raspberry Pi Clock to the DS3231.")
            self.rtc_ext_sync_rpi()
            print("[OK]")

    def rtc_ext_sync_rpi(self):
        """Synchronize the Raspberry Pi Date and Time to the DS3231 External RTC

        Parameters
        ----------
        none

        Returns:
        --------
        none

        """
        # TODO Check for success and return that result
        # 1. Read the external RTC Date and Time
        ext_rtc_time = self._rtc_ext.disp_time(verbose=False)
        # 2. Compose the command to set the RPi Date and Time
        cmd = "sudo date -s " + "\"" + ext_rtc_time + "\""
        # 3. Execute the cmd
        os.system(cmd)

    def rtc_ext_sync_ext(self):
        """Synchronize the DS3231 External RTC Date and Time to the Raspberry Pi

        Parameters
        ----------
        none

        Returns:
        --------
        bool success : True if successful, False if an error occurred

        """

        # Get the current Raspberry Pi time
        rpi_datetime = datetime.datetime.now()

        # Format the Raspberry Pi date/time for input to ds3231 set_time() method
        date_str = "%04d/%02d/%02d %02d:%02d:%02d" % (rpi_datetime.year, rpi_datetime.month, rpi_datetime.day,
                                                      rpi_datetime.hour, rpi_datetime.minute, rpi_datetime.second)

        # Synchronize the external DS3231 RTC to the Raspberry Pi Date/Time
        success = self._rtc_ext.set_time(date_str)

        return success


    def read_samp_num(self):
        """Read the sample number from the samp_num pickle file.
        Creates and initializes a samp_num pickle file if it does not exist.

        Parameters
        ----------
        none

        Returns:
        --------
        int samp_num : Sample Number

        """
        # If the samp_num.pkl file exists, we can open and read the contents
        try:
            with open(samp_num_pickle_file, "rb") as pickle_file:
                samp_num = pickle.load(pickle_file)

        # This must be the first time through so the pickle file does not yet exist
        except:
            print("\n\rCould not find the samp_num pickle file.  Creating... ")
            samp_num = 0
            with open(samp_num_pickle_file, "wb") as pickle_file:
                pickle.dump(samp_num, pickle_file)

        return samp_num

    def increment_samp_num(self):
        """Increment the sample number in the samp_num pickle file.
        Creates and initializes a samp_num pickle file if it does not exist.

        Parameters
        ----------
        none

        Returns:
        --------
        int samp_num : Sample Number

        """

        # If the samp_num.pkl file exists, we can open and read the contents
        try:
            with open(samp_num_pickle_file, "rb") as pickle_file:
                samp_num = pickle.load(pickle_file)
            samp_num += 1
            with open(samp_num_pickle_file, "wb") as pickle_file:
                pickle.dump(samp_num, pickle_file)

        except:
            print("\n\rCould not find the samp_num pickle file.  Creating... ")
            samp_num = 0
            with open(samp_num_pickle_file, "wb") as pickle_file:
                pickle.dump(samp_num, pickle_file)

        return samp_num

    def delete_samp_num_pickle(self):
        """Delete the Sample Number Pickle File

        Parameters
        ----------
        none

        Returns:
        --------
        none

        Example:
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.delete_data_xmt_status_pickle()
        """

        if os.path.exists(samp_num_pickle_file):
            os.remove(samp_num_pickle_file)
            print('[OK] Sample Number Pickle File Removed.')
        else:
            print("[OK] Sample Number Pickle File Already Removed or Does Not Exist.")

