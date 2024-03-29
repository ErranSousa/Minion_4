import os
import pickle
import sys  # for sys.path
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox
from minion_hat import MinionHat
sys.path.insert(0, '/home/pi/Documents/Minion_scripts/')
from minsat import MinSat

# MinSat Board Settings
gps_port = "/dev/ttySC0"
gps_baud = 9600
modem_port = "/dev/ttySC1"
modem_baud = 19200

# Sets the Final Sample Status Flag to False
#    False : Final Samples Not Performed
#    True  : Final Samples Were Performed
try:
    with open("/home/pi/Documents/Minion_scripts/final_samp_status.pkl", "wb") as final_samp_status_fid:
        final_sample_status_flag = False
        pickle.dump(final_sample_status_flag, final_samp_status_fid)
    print("[OK] Set Final Sample Status Flag to False")
except FileNotFoundError:
    print("[Error] Could Not Set the Final Sample Status Flag to False")

# create an instance of MinionToolbox() called minion_tools
minion_tools = MinionToolbox()

# Create an instance of MinionHat()
minion_hat = MinionHat()

# Create an instance of MinSat()
minion_sat = MinSat(gps_port, gps_baud, modem_port, modem_baud)

# Delete the Data Transmit Status Pickle prior to mission start
minion_tools.delete_data_xmt_status_pickle()

# Delete the Sample Number Pickle (samp_num.pkl) prior to mission start
minion_tools.delete_samp_num_pickle()

# Delete the Mission Start Time Pickle file
minion_tools.delete_mission_start_time_pickle()

# Reset the Burn Wire
minion_hat.burn_wire(minion_hat.DISABLE)
print('[OK] Disabled the Burn Wire')

# Reset the Recovery Strobe
minion_hat.strobe(minion_hat.DISABLE)
print('[OK] Disabled the Recovery Strobe')

# Power Down the GPS Module
minion_sat.gps_pwr(minion_sat.dev_off)
print('[OK] Powered Down the GPS Module')

# Power Down the Iridium Modem
minion_sat.modem_pwr(minion_sat.dev_off)
print('[OK] Powered Down the Iridium Modem')

time = os.popen('ls /home/pi/Desktop/minion_data/INI/1-*.txt').read()

time = time.strip('/home/pi/Desktop/minion_data/INI/1-')

time = time.strip('_TEMPPRES-INI.txt\n')

num_mem = int(len(os.listdir("/home/pi/Desktop/minion_memory/"))) + 1

save_dir = '/home/pi/Desktop/minion_memory/{}-{}'.format(num_mem, time)

os.system('sudo mkdir {}'.format(save_dir))

os.system('sudo mv /home/pi/Desktop/minion_data/ /home/pi/Desktop/minion_pics/ {}'.format(save_dir))

os.system('sudo cp /home/pi/Desktop/Minion_config.ini {}'.format(save_dir))

os.system('sudo mkdir /home/pi/Desktop/minion_data/ /home/pi/Desktop/minion_pics/')

os.system('sudo mkdir /home/pi/Desktop/minion_data/INI/ /home/pi/Desktop/minion_data/FIN/')

dir_name = save_dir.strip('/home/pi/Desktop/minion_memory/')

print('[OK] Files are saved to {}'.format(dir_name))
