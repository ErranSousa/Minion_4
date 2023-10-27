#!/usr/bin/python3

import time
import serial
import argparse
import sys
import pickle
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox
import tsys01  # temperature sensor
import ms5837  # 30bar pressure sensor
from kellerLD import KellerLD  # 100bar pressure sensor


def init_serial():
    # Set up the serial port
    ser_object = serial.Serial(
        port='/dev/serial0',  # serial port the object should read
        baudrate=19200,  # rate at which information is transferred over comm channel
        parity=serial.PARITY_NONE,  # no parity checking
        stopbits=serial.STOPBITS_ONE,  # pattern of bits to expect which indicates the end of a character
        bytesize=serial.EIGHTBITS,  # number of data bits
        timeout=1
    )
    return ser_object


def init_oxybase():
    print('[ OXY ] Initializing OxyBase Sensor. Requires ~5 seconds.')
    GPIO.output(pin_defs_dict['OXYBASE_EN'], GPIO.HIGH)  # Power ON
    time.sleep(4)  # 4 second warm-up
    ser.flushInput()  # Flush  I/O buffers
    ser.flushOutput()
    ser.write(b'mode0001\r')  # Send Mode Command
    time.sleep(1)
    print('[ OXY ] OxyBase Sensor Initialized.')


def get_oxybase():
    # Request Data
    ser.write(b'data\r')
    data = ser.read_until('\r')

    return data


def init_tsys01():
    status = False
    sensor_temp = tsys01.TSYS01()
    # Initialize the sensor
    try:
        sensor_temp.init()
        status = True
    except:
        print('[ TSYS01 ] Failed to initialize the TSYS01 temperature sensor')

    return sensor_temp, status


def get_tsys01(tsys01_obj):
    try:
        tsys01_obj.read()
        temp = round(tsys01_obj.temperature(), 2)
        temp = "%07.3f" % temp  # fix field length by prepending zeros if necessary
    except:
        print('[ TSYS01 ] Failed to read the sensor')
        temp = 'NaN'

    return temp


def init_psense_30bar():
    status = False
    sensor_psense_30bar = ms5837.MS5837_30BA()
    try:
        status = sensor_psense_30bar.init()
    except:
        print("[ br30 ] Failed to initialize Bar30 pressure sensor!")

    return sensor_psense_30bar, status


def get_psense_30bar(psense_30bar_obj):
    try:
        psense_30bar_obj.read()
        meas_30bar_press = round((psense_30bar_obj.pressure(ms5837.UNITS_mbar) * mbar_to_dbar) - psense_30bar_surface_offset, 3)
        meas_30bar_press = "%07.3f" % meas_30bar_press  # fix field length by prepending zeros if necessary
        meas_30bar_temp = round(psense_30bar_obj.temperature(ms5837.UNITS_Centigrade), 2)
        meas_30bar_temp = "%07.3f" % meas_30bar_temp  # fix field length by prepending zeros if necessary
    except:
        print('[ br30 ] Failed to read the sensor')
        meas_30bar_press = 'NaN'
        meas_30bar_temp = 'NaN'

    return meas_30bar_press, meas_30bar_temp


def init_psense_100bar():
    status = False
    sensor_psense_100bar = KellerLD()
    try:
        status =  sensor_psense_100bar.init()
    except:
        print("[ br100 ] Failed to initialize Bar100 pressure sensor!")

    return sensor_psense_100bar, status


def get_psense_100bar(psense_100bar_obj):
    try:
        psense_100bar_obj.read()
        meas_100bar_press = round((psense_100bar_obj.pressure() * bar_to_dbar) - psense_100bar_surface_offset, 3)
        meas_100bar_press = "%07.3f" % meas_100bar_press  # fix field length by prepending zeros if necessary
        meas_100bar_temp = round(psense_100bar_obj.temperature(), 2)
        meas_100bar_temp = "%07.3f" % meas_100bar_temp  # fix field length by prepending zeros if necessary
    except:
        print('[ br100 ] Failed to read the sensor')
        meas_100bar_press = 'NaN'
        meas_100bar_temp = 'NaN'

    return str(meas_100bar_press), meas_100bar_temp


def test_sensors():
    # Test the OxyBase Sensor
    ser.flushInput()  # Flush  I/O buffers
    ser.flushOutput()
    ser.write(b'data\r')
    oxy_data = ser.read_until('\r')
    print('[ OXY ] ' + oxy_data.decode('utf-8').strip())
    time.sleep(1)
    ser.write(b'mode0000\r')
    GPIO.output(pin_defs_dict['OXYBASE_EN'], GPIO.LOW)

    # Test Temperature (TSYS01)
    if args.temperature:
        test_sensor_tsys01, init_success = init_tsys01()
        if init_success:
            test_temp_tsys01 = get_tsys01(test_sensor_tsys01)
            print("[ TSYS01 ] {} C".format(test_temp_tsys01))  # degrees Celsius

    # Test the 30bar Pressure Sensor
    if args.press_30bar:
        test_sensor_30bar, init_success_30bar = init_psense_30bar()
        if init_success_30bar:
            test_30bar_press, test_30bar_temp = get_psense_30bar(test_sensor_30bar)
            print('[ br30 ] ' + str(test_30bar_press) + ' dbar, ' + str(test_30bar_temp) + ' degC')

    # Test the 100bar Pressure Sensor
    if args.press_100bar:
        test_sensor_100bar, init_success_100bar = init_psense_100bar()
        if init_success_100bar:
            test_100bar_press, test_100bar_temp = get_psense_100bar(test_sensor_100bar)
            print('[ br100 ] ' + str(test_100bar_press) + ' dbar, ' + str(test_100bar_temp) + ' degC')


if __name__ == '__main__':

    # Initializations
    bar_to_dbar = 10
    psense_100bar_surface_offset = 0
    mbar_to_dbar = .01
    psense_30bar_surface_offset = 10

    # Enables or disables the OxyBase continuous loop
    run_oxy_pickle_name = '/home/pi/Documents/Minion_scripts/run_oxy_state.pickle'

    # Create an instance of MinionToolbox()
    minion_tools = MinionToolbox()  # create an instance of MinionToolbox() called minion_tools

    # Load the Data Configuration Directory
    data_config = minion_tools.read_data_config()

    # Get the current time stamp information
    samp_time = minion_tools.update_timestamp()

    # Configure the Raspberry Pi GPIOs
    GPIO, pin_defs_dict = minion_tools.config_gpio()

    # Load the Dictionary of Data File Types (for writing the header)
    data_type_dict = minion_tools.data_type_dict()

    # Create an instance of the argument parser
    parser = argparse.ArgumentParser()

    # Add Arguments:
    parser.add_argument('-m', '--mode',
                        help='Sampling Mode: TEST, CONT')
    parser.add_argument('-p', '--period',
                        help='Sampling Period in seconds')
    parser.add_argument('-t', '--temperature',
                        help='Enable Temperature Measurements', action='store_true')
    parser.add_argument('-br30', '--press_30bar',
                        help='Enable 30 bar Pressure Sensor Measurements', action='store_true')
    parser.add_argument('-br100', '--press_100bar',
                        help='Enable 100 bar Pressure Sensor Measurements', action='store_true')

    # Parse the arguments
    args = parser.parse_args()
    # print(args)

    # Initialize the serial port
    ser = init_serial()

    if args.mode.upper() == 'TEST':
        init_oxybase()
        test_sensors()
        exit(0)

    elif args.mode.upper() == 'CONT':

        if args.period is None:
            print('Sample period is required for continuous mode')
            exit(0)

        print('Continuous Mode with {} second period.'.format(args.period))
        continuous_mode_file_name = '000-{}_OXY_CONT.txt'.format(samp_time)
        continuous_mode_file_path_name = "{}/minion_data/".format(data_config['Data_Dir']) + continuous_mode_file_name

        # Compose the meta-record, column headers & write them to the file
        meta_record = data_type_dict['CONT_Oxy'] + ',' + continuous_mode_file_name + ',' + str(args.period)
        variable_names = 'epoch_secs;addr;amplitude;phase;temperature;oxygen;error;'

        if args.temperature:
            variable_names = variable_names + 'temp_TSYS01;'
            sensor_tsys01, init_status_tsys01 = init_tsys01()
        if args.press_30bar:
            variable_names = variable_names + 'press_30bar;temp_30bar;'
            sensor_30bar, init_status_30bar = init_psense_30bar()
        if args.press_100bar:
            variable_names = variable_names + 'press_100bar;temp_100bar;'
            sensor_100bar, init_status_100bar = init_psense_100bar()
        print(variable_names)

        with open(continuous_mode_file_path_name, "a+") as file:
            file.write(meta_record)
            file.write('\r' + variable_names)

        # Create and update a pickle file.  This pickle file tracks if the loop should be running.
        # To end the continuous mode sampling use the end_oxy.py or the alias end-oxy
        run_oxy = True
        with open(run_oxy_pickle_name, 'wb') as pickle_file_fid:
            pickle.dump(run_oxy, pickle_file_fid)

        init_oxybase()
        ser.flushInput()  # Flush  I/O buffers
        ser.flushOutput()

        # Sampling Loop
        while True:
            tm_0 = time.perf_counter()

            # Check if the loop should be running (ended with end_oxy.py)
            with open(run_oxy_pickle_name, 'rb') as pickle_file_fid:
                run_oxy_state = pickle.load(pickle_file_fid)
            if not run_oxy_state:
                break

            # OxyBase Sample
            oxy_data = get_oxybase()

            # UNIX Epoch seconds timestamp
            tm_stamp = int(time.time())

            # Compose the data string, prepending a UNIX Epoch seconds timestamp
            data_string = str(tm_stamp) + ';' + oxy_data.decode('utf-8').strip()

            # Get TSYS01 Temperature
            if args.temperature:
                if init_status_tsys01:
                    tsys01_temp = get_tsys01(sensor_tsys01)
                    data_string = data_string + tsys01_temp + ';'
                else:
                    data_string = data_string + 'NaN;'

            # Get the Pressure & Temperature from the 30 Bar Pressure Sensor
            if args.press_30bar:
                if init_status_30bar:
                    psense_30bar_press, psense_30bar_temp = get_psense_30bar(sensor_30bar)
                    data_string = data_string + str(psense_30bar_press) + ';' + str(psense_30bar_temp) + ';'
                else:
                    data_string = data_string + 'NaN;'

            # Get the Pressure & Temperature from the 100 Bar Pressure Sensor
            if args.press_100bar:
                if init_status_100bar:
                    psense_100bar_press, psense_100bar_temp = get_psense_100bar(sensor_100bar)
                    data_string = data_string + str(psense_100bar_press) + ';' + str(psense_100bar_temp) + ';'
                else:
                    data_string = data_string + 'NaN;'

            # Write the data to the file
            with open(continuous_mode_file_path_name, "a+") as file:
                file.write('\r' + data_string)

            print(data_string)

            tm_sample = time.perf_counter() - tm_0
            if tm_sample >= float(args.period):
                tm_sample = float(args.period)

            time.sleep(float(args.period) - tm_sample)

        # Sensor shutdown
        ser.write(b'mode0000\r')
        GPIO.output(pin_defs_dict['OXYBASE_EN'], GPIO.LOW)
        print('Sampling Complete.')

    else:
        print('[ ERROR ] Unknown Mode: ' + args.mode)
        exit(0)
