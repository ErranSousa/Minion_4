# import minsat
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_scripts/')
from minsat import MinSat
# import sys, os
import subprocess
from minion_toolbox import MinionToolbox

# MinSat Board Settings
gps_port = "/dev/ttySC0"
gps_baud = 9600
modem_port = "/dev/ttySC1"
modem_baud = 19200

ex_msg = "Transmitting a Test Message via Iridium"

print("-"*len(ex_msg))
print(ex_msg)
print("-"*len(ex_msg))

sys.stdout.flush()

# Create an istance of the MinionToolbox
minion_tools = MinionToolbox()
sys.stdout.flush()

# Load the Minion Configuration
minion_mission_config = minion_tools.read_mission_config()

# Create an instance of the MinSat Class
m1 = MinSat(gps_port, gps_baud, modem_port, modem_baud)
sys.stdout.flush()

message1 = 'This is Minion ' + minion_mission_config['Minion_ID']

print('Sending Message: ' + message1)
sys.stdout.flush()

resp = m1.sbd_send_message(message1)

# Ensure that the modem is powered down
m1.modem_pwr(m1.dev_off)
