import time
import serial
import argparse
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox


def sensor_setup():
    GPIO.output(pin_defs_dict['OXYBASE_EN'], GPIO.HIGH)  # Power ON
    time.sleep(4)  # 4 second warm-up
    ser.flushInput()  # Flush  I/O buffers
    ser.flushOutput()
    ser.write(b'mode0001\r')  # Send Mode Command
    time.sleep(1)


def test_sensor():
    sensor_setup()
    ser.flushInput()  # Flush  I/O buffers
    ser.flushOutput()
    ser.write(b'data\r')
    data = ser.read_until('\r')
    print(data.decode('utf-8').strip())
    time.sleep(1)
    ser.write(b'mode0000\r')
    GPIO.output(pin_defs_dict['OXYBASE_EN'], GPIO.LOW)


tic = time.perf_counter()
samp_counter = 0

# Create an instance of MinionToolbox()
minion_tools = MinionToolbox()  # create an instance of MinionToolbox() called minion_tools

# Configure the Raspberry Pi GPIOs
GPIO, pin_defs_dict = minion_tools.config_gpio()

# Load the Minion Configuration
minion_mission_config = minion_tools.read_mission_config()

# Load the Data Configuration Directory
data_config = minion_tools.read_data_config()

# Get the current time stamp information
samp_time = minion_tools.update_timestamp()

# Get the current sample number
samp_num = minion_tools.read_samp_num()

# Minion Mission Configuration file
configLoc = '{}/Minion_config.ini'.format(data_config['Data_Dir'])

# Load the Dictionary of Data File Types (for writing the header)
data_type_dict = minion_tools.data_type_dict()

# Create an instance of the argument parser
parser = argparse.ArgumentParser()

# Add Arguments:
parser.add_argument('-m', '--mode', help='Sampling Mode: TEST, INI, TLP or FIN')

# Parse the arguments
args = parser.parse_args()

# Initializations:
reply = ''

# Set up the serial port
ser = serial.Serial(
    port='/dev/serial0',            # serial port the object should read
    baudrate=19200,                 # rate at which information is transferred over comm channel
    parity=serial.PARITY_NONE,      # no parity checking
    stopbits=serial.STOPBITS_ONE,   # pattern of bits to expect which indicates the end of a character
    bytesize=serial.EIGHTBITS,      # number of data bits
    timeout=1
)

# Set up sampling and data logging based on sampling mode
if args.mode.upper() == 'TEST':
    test_sensor()
    exit(0)

elif args.mode.upper() == 'INI':
    print('[ OXY ] Initial Sampling Mode')
    DATA_TYPE = data_type_dict['INI_Oxy']  # Initial Sampling Type Data for Oxygen
    total_samples = (minion_mission_config['INIsamp_hours'] * 3600) / minion_mission_config['INIsamp_oxygen_period']
    sample_period = minion_mission_config['INIsamp_oxygen_period']

    samp_num_leading_zeros = "%03d" % samp_num

    samp_time = "{}-{}".format(samp_num_leading_zeros, samp_time)  # Add leading zeros to sample count

    file_name = "{}_OXY-INI.txt".format(samp_time)

    file_path_name = "{}/minion_data/INI/".format(data_config['Data_Dir']) + file_name

elif args.mode.upper() == 'TLP':
    print('[ OXY ] Time Lapse Sampling Mode')
    DATA_TYPE = data_type_dict['TLP_Oxy']  # Time Lapse Sampling Type Data for Oxygen
    total_samples = (minion_mission_config['TLPsamp_burst_minutes'] * 60) / minion_mission_config['TLPsamp_oxygen_period']
    sample_period = minion_mission_config['TLPsamp_oxygen_period']

    samp_num_leading_zeros = "%03d" % samp_num

    samp_time = "{}-{}".format(samp_num_leading_zeros, samp_time)  # Add leading zeros to sample count

    file_name = "{}_OXY-TLP.txt".format(samp_time)

    file_path_name = "{}/minion_data/".format(data_config['Data_Dir']) + file_name

elif args.mode.upper() == 'FIN':
    print('[ OXY ] Final Sampling Mode')
    DATA_TYPE = data_type_dict['FIN_Oxy']  # Final Sampling Type Data for Oxygen
    total_samples = (minion_mission_config['FINsamp_hours'] * 3600) / minion_mission_config['FINsamp_oxygen_period']
    sample_period = minion_mission_config['FINsamp_oxygen_period']

    samp_num_leading_zeros = "%03d" % samp_num

    samp_time = "{}-{}".format(samp_num_leading_zeros, samp_time)  # Add leading zeros to sample count

    file_name = "{}_OXY-FIN.txt".format(samp_time)

    file_path_name = "{}/minion_data/FIN/".format(data_config['Data_Dir']) + file_name

else:
    print('[ OXY ] Unknown Sample Mode.  Exiting.')
    total_samples = 0
    sample_period = 0
    file_path_name = ''
    exit(0)

# Compose the meta-record
file_header = DATA_TYPE + ',' + file_name + ',' + str(sample_period) + 'sec'

# print('[ OXY ] Total Samples: ' + str(total_samples))
# print('[ OXY ] Sample Period: ' + str(sample_period) + ' seconds')
# print('[ OXY ] File Name: ' + file_name)
# print('[ OXY ] File Name Full Path: ' + file_path_name)
# print('[ OXY ] Data Type: ' + DATA_TYPE)
# print('[ OXY ] File Header: ' + file_header)

print("[ OXY ] Port Power ON")
GPIO.output(pin_defs_dict['OXYBASE_EN'], GPIO.HIGH)

# Wait 4-sec before sending commands
print('[ OXY ] OXYBase requires a ~4 second warmup before sending commands')
time.sleep(4)

print('[ OXY ] Sending commands...')

# Ensure that the serial port buffers are cleared
ser.flushInput()
ser.flushOutput()

# Mode 1 (H2M Communication)
ser.write(b'mode0001\r')
time.sleep(1)

# Ensure that the serial port buffers are cleared
ser.flushInput()
ser.flushOutput()

# Write the meta-record
with open(file_path_name, "a+") as file:
    file.write(file_header)
start = time.perf_counter()
print('Total Setup time: ' + str(start-tic))

while samp_counter < total_samples:

    tic = time.perf_counter()

    # Request Data
    ser.write(b'data\r')

    # Read the response
    reply = ser.read_until('\r')

    # Write the data to the file
    with open(file_path_name, "a+") as file:
        file.write('\r' + reply.decode('utf-8').strip())

    print('[ OXY ] ' + reply.decode('utf-8').strip())

    # Increment the sample number
    samp_counter += 1

    timeS = time.perf_counter() - tic

    if timeS >= sample_period:
        timeS = sample_period

    time.sleep(sample_period - timeS)

ser.write(b'mode0000\r')
print("[ OXY ] Port Power OFF")
GPIO.output(pin_defs_dict['OXYBASE_EN'], GPIO.LOW)
