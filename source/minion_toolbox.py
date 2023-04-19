#!/usr/bin/env python3

"""! @brief API Set for Commonly Used Functionality in the Minion

"""
from __future__ import division  # Ensures Python3 division rules
import configparser
import os
import sys
import pickle
# import RPi.GPIO as GPIO
import RPi.GPIO
import time
import datetime
from ds3231 import DS3231

# Pin Definitions
light = 12

GPIO = RPi.GPIO

data_config_file = '/home/pi/Documents/Minion_scripts/Data_config.ini'
pin_defs_file = '/home/pi/Documents/Minion_tools/pin_defs.ini'
data_xmt_status_pickle_file = '/home/pi/Documents/Minion_scripts/data_xmt_status.pickle'
samp_num_pickle_file = '/home/pi/Documents/Minion_scripts/samp_num.pkl'
time_stamp_pickle_file = '/home/pi/Documents/Minion_scripts/timesamp.pkl'
mission_start_pickle_file = '/home/pi/Documents/Minion_scripts/mission_start_time.pkl'

# Command Aliases for Wifi
ifswitch = "sudo python /home/pi/Documents/Minion_tools/dhcp-switch.py"
iwlist = 'sudo iwlist wlan0 scan | grep -e "Minion_Hub" -e "Master_Hub"'
net_cfg = "ls /etc/ | grep dhcp"


class MinionToolbox(object):

    def __init__(self):
        self._py_ver_major = sys.version_info.major
        self._rtc_ext = DS3231()
        # self.GPIO = RPi.GPIO

    # str2bool will be depricated!!!  Use ans2bool()
    def str2bool(self, v):
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

    def ans2bool(self, ans2convert):
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

    def check_wifi(self, IgnoreStatus):
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
                # print("You have Minions!")
                pass

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

        # print('Data Config: ' + data_config['Data_Dir'])
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
                int TLPsamp_hours : Duration of Time Lapse Mode Sampling in hours
                float Srate : Sleep Cycle
                float TLPsamp_burst_minutes : Duration of a sample burst in Time-Lapse Mode
                int TLPsamp_interval_minutes : Time between sample bursts in Time-Lapse Mode
                float TLPsamp_tempPress_rate : Temperature / Pressure Sample Rate (Time-Lapse Mode)
                float TLPsamp_oxygen_rate : Oxygen Sample Rate (Time-Lapse Mode)
                bool iniImg : Enable / Disable Image Capture
                bool iniP30 : Enable / Disable 30 Bar Pressure Sensor
                bool iniP100 : Enable / Disable 100 Bar Pressure Sensor
                bool iniTmp : Enable/Disable Temperature Sensor
                bool iniO2 : Enable/Disable Oxygen Sensor
                bool iniAcc : Enable/Disable Accelerometer


        """

        # list of keys
        keys = ['Minion_ID', 'Abort', 'MAX_Depth', 'IG_WIFI_D', 'IG_WIFI_H',
                'INIsamp_hours', 'INIsamp_camera_rate', 'INIsamp_tempPres_rate',
                'INIsamp_oxygen_rate', 'FINsamp_hours', 'FINsamp_camera_rate',
                'FINsamp_tempPres_rate', 'FINsamp_oxygen_rate', 'TLPsamp_tempPress_rate',
                'TLPsamp_oxygen_rate', 'TLPsamp_hours', 'TLPsamp_burst_minutes', 'TLPsamp_interval_minutes',
                'Srate', 'iniImg', 'iniP30', 'iniP100', 'iniTmp', 'iniO2'
                ]

        mission_config = dict.fromkeys(keys)

        data_config = self.read_data_config()
        config_file = '{}/Minion_config.ini'.format(data_config['Data_Dir'])
        # print('Mission Config: ' + config_file)

        config = configparser.ConfigParser()
        config.read(config_file)

        mission_config['Minion_ID'] = str(config['MINION']['number'])

        mission_config['Abort'] = self.str2bool(config['Mission']['abort'])
        mission_config['MAX_Depth'] = float(config['Mission']['max_depth'])
        mission_config['IG_WIFI_D'] = float(config['Mission']['ignore_wifi-days'])
        mission_config['IG_WIFI_H'] = float(config['Mission']['ignore_wifi-hours'])

        mission_config['INIsamp_hours'] = float(config['Initial_Samples']['hours'])
        mission_config['INIsamp_camera_rate'] = float(config['Initial_Samples']['camera_sample_rate'])
        mission_config['INIsamp_tempPres_rate'] = float(config['Initial_Samples']['temppres_sample_rate'])
        mission_config['INIsamp_oxygen_rate'] = float(config['Initial_Samples']['oxygen_sample_rate'])

        mission_config['FINsamp_hours'] = float(config['Final_Samples']['hours'])
        mission_config['FINsamp_camera_rate'] = float(config['Final_Samples']['camera_sample_rate'])
        mission_config['FINsamp_tempPres_rate'] = float(config['Final_Samples']['temppres_sample_rate'])
        mission_config['FINsamp_oxygen_rate'] = float(config['Final_Samples']['oxygen_sample_rate'])

        # mission_config['Ddays'] = int(config['Deployment_Time']['days'])
        mission_config['TLPsamp_hours'] = int(config['Time_Lapse_Samples']['hours'])

        mission_config['Srate'] = float(config['Sleep_cycle']['minion_sleep_cycle'])

        tlp_samp_burst_minutes = config['Time_Lapse_Samples']['sample_burst_duration']
        # Determine if the value entered into 'sample_burst_duration' is
        #    'Camera' or an actual number.
        # Note: Any text will work, not just 'Camera'
        try:
            mission_config['TLPsamp_burst_minutes'] = float(tlp_samp_burst_minutes)
        except:
            # Since tlp_samp_burst_minutes cannot be cast as a float, there must be some text
            # in the field such as 'Camera'
            mission_config['TLPsamp_burst_minutes'] = float(.2)
        mission_config['TLPsamp_tempPress_rate'] = float(config['Time_Lapse_Samples']['temppres_sample_rate'])
        mission_config['TLPsamp_oxygen_rate'] = float(config['Time_Lapse_Samples']['oxygen_sample_rate'])
        mission_config['TLPsamp_interval_minutes'] = int(config['Time_Lapse_Samples']['sample_interval_minutes'])

        mission_config['iniImg'] = self.str2bool(config['Sampling_scripts']['image'])
        mission_config['iniP30'] = self.str2bool(config['Sampling_scripts']['30ba-pres'])
        mission_config['iniP100'] = self.str2bool(config['Sampling_scripts']['100ba-pres'])
        mission_config['iniTmp'] = self.str2bool(config['Sampling_scripts']['temperature'])
        mission_config['iniO2'] = self.str2bool(config['Sampling_scripts']['oxybase'])
        # mission_config['iniAcc'] = self.str2bool(config['Sampling_scripts']['acc_100hz'])

        return mission_config

    def write_mission_config_option(self, section, option, value):
        """Set an option in the mission config file.

         Parameters
         ----------
         section : string
             Configuration Section
         option : string
             Configuration Option
         value : string
             Configuration Value

         Returns:
         --------
         none
         """
        # Read the location of the mission configuration file
        data_config = self.read_data_config()
        config_file = '{}/Minion_config.ini'.format(data_config['Data_Dir'])

        mission_config = configparser.ConfigParser()
        mission_config.read(config_file)

        # Set the option
        mission_config.set(section, option, value)

        # Write the mission to the file
        with open(config_file, 'w') as configFile:
            mission_config.write(configFile)


    def config_gpio(self, **kwargs):
        """Reads the pin_config.ini file, configures pin directions and default states.
        Returns a dictionary with pin names & assignments

        Keyword Args:
        -------------
        verbose : displays additional information (default False)
        defaults : Configures the pins to their default states as listed in pin_defs.ini (default False)

        Returns:
        --------
        GPIO : An instance of RPi.GPIO
        dict pin_defs_dict : Minion Pin Definitions Dictionary
            keys:
                based on pin_defs.ini

        Example: Configure the GPIOs and configure their default states
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            GPIO, pin_defs_dict = minion_tools.config_gpio(defaults=True, verbose=True)

        Example: Configure the GPIOs and toggle the Green LED
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            import time
            GPIO, pin_defs_dict = minion_tools.config_gpio()
            GPIO.output(pin_defs_dict['LED_GRN'], GPIO.HIGH)
            time.sleep(1)
            GPIO.output(pin_defs_dict['LED_GRN'], GPIO.LOW)
        """

        options = {
            'verbose': False,
            'defaults': False
        }
        options.update(kwargs)

        parser = configparser.ConfigParser()
        parser.read(pin_defs_file)

        # Create an empty dictionary
        pin_defs_dict = dict()

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        for sect in parser.sections():
            pin_defs_dict[sect] = int(parser.get(sect, 'pin'))
            if parser.get(sect, 'direction').upper() == 'IN':
                if options['verbose']:
                    print('Configuring {} pin {} as an input'.format(sect, parser.get(sect, 'pin')))
                GPIO.setup(int(parser.get(sect, 'pin')), GPIO.IN)
            if parser.get(sect, 'direction').upper() == 'OUT':
                if options['verbose']:
                    print('Configuring {} pin {} as an output'.format(sect, parser.get(sect, 'pin')))
                GPIO.setup(int(parser.get(sect, 'pin')), GPIO.OUT)
            if parser.get(sect, 'direction').upper() == 'OUT' and options['defaults']:
                if options['verbose']:
                    print('Configuring {} pin {} default state as {}'.format(sect, parser.get(sect, 'pin'), parser.get(sect, 'default_state')))
                GPIO.output(int(parser.get(sect, 'pin')), int(parser.get(sect, 'default_state')))

        return GPIO, pin_defs_dict

    def update_timestamp(self):
        """Updates the timesamp pickle file

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
            time_stamp = tm_now_dict['YYYY'] + "-" + tm_now_dict['MM'] + "-" + tm_now_dict['DD'] + "_" + tm_now_dict[
                'hh'] + "-" + tm_now_dict['mm'] + "-" + tm_now_dict['ss']

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

    def flash(self, num_flashes, ton, toff):
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
            minion_tools.flash(2,250,250)

        Example: Simply illuminates the LED Ring for 2 seconds

            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.flash(1,2000,0)

        Example: Dimmable Setting

            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.flash(100,5,5)#Dim by 50%
        
        """

        gpio_pins, pin_defs_dict = self.config_gpio()

        for val in range(num_flashes):
            gpio_pins.output(pin_defs_dict['LED_RING_CTRL'], GPIO.HIGH)
            time.sleep(ton / 1000)
            # If we have done the requisite number of flashes,
            # no need for the final off time.
            if val == num_flashes - 1:
                break
            gpio_pins.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)
            time.sleep(toff / 1000)

        # Finally, turn off the LED Ring
        gpio_pins.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)

    def kill_sampling(self, scriptNames):
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

    def write_data_file_header(self, data_type, file_path_name, file_name, samp_rate, iniP30, iniP100, iniTmp):
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

        with open(file_path_name, "a+") as file:

            file.write(data_type)  # Write Data Type Identifier
            file.write("," + file_name)  # Write the file name
            file.write("," + str(samp_rate))  # Write the sample rate

            if iniP30 == True:
                # file.write("Pressure(dbar),Temp(C)")
                file.write(",Pressure(dbar*1000),Temp(C*100)")  # Meta-Record for fixed field Press and Temp

            if iniP100 == True:
                # file.write("Pressure(dbar),Temp(C)")
                file.write(",Pressure(dbar*1000),Temp(C*100)")  # Meta-Record for fixed field Press and Temp

            if iniTmp == True:
                # file.write(", TempTSYS01(C)")
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

    def read_mission_start_time(self):
        """Read the mission start time from the mission start time pickle file.
        Creates and initializes the pickle file if it does not exist.

        Parameters
        ----------
        none

        Returns:
        --------
        datetime.datetime mission_start_time : Time that the mission was started

        """

        # If the pkl file exists, we can open and read the contents
        try:
            with open(mission_start_pickle_file, "rb") as pickle_file:
                mission_start_time = pickle.load(pickle_file)

        # This must be the first time through so the pickle file does not yet exist
        except FileNotFoundError:
            print("\n\rCould not find the mission start time pickle file.  Initializing... ")
            mission_start_time = datetime.datetime.now()
            with open(mission_start_pickle_file, "wb") as pickle_file:
                pickle.dump(mission_start_time, pickle_file)
            print("[OK] Created sample number pickle file.")

        return mission_start_time

    def delete_mission_start_time_pickle(self):
        """Delete the Mission Start Time Pickle File

        Parameters
        ----------
        none

        Returns:
        --------
        none

        Example:
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            minion_tools.delete_mission_start_time_pickle()
        """
        if os.path.exists(mission_start_pickle_file):
            os.remove(mission_start_pickle_file)
            print('[OK] Mission Start Time Pickle File Removed.')
        else:
            print("[OK] Mission Start Time Pickle File Already Removed or Does Not Exist.")

    def ignore_wifi_check(self):
        """Checks if WIFI should be ignored

        Parameters
        ----------
        none

        Returns:
        --------
        bool ignore_wifi_status : True if ignoring wifi, False looking for wifi

        Example:
            from minion_toolbox import MinionToolbox
            minion_tools = MinionToolbox()
            ignore_wifi_status = minion_tools.ignore_wifi_check()
        """

        # Read the mission configuration
        mission_config = self.read_mission_config()

        # Read the mission start time - creates the pickle if it does not exist
        mission_start_time = self.read_mission_start_time()

        # Calculate the until the wifi should no longer be ignored
        ignore_wifi_until = mission_start_time + datetime.timedelta(hours=mission_config['IG_WIFI_H'])

        # Check if we have reached the time to start detecting wifi
        if datetime.datetime.now() >= ignore_wifi_until:
            print("Looking for Wifi")
            ignore_wifi_status = False
        else:
            print('Ignoring wifi')
            ignore_wifi_status = True

        return ignore_wifi_status

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
            print("[OK] Created sample number pickle file.")

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
