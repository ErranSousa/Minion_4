#!/usr/bin/env python

import os
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

# create an instance of MinionToolbox()
minion_tools = MinionToolbox()

# Delete the Sample Number Pickle (samp_num.pkl) prior to mission start
minion_tools.delete_samp_num_pickle()

os.system('sudo rm -r /home/pi/Desktop/minion_pics/*')
os.system('sudo rm -r /home/pi/Desktop/minion_data/*.txt')
os.system('sudo rm -r /home/pi/Desktop/minion_data/INI/*')
os.system('sudo rm -r /home/pi/Desktop/minion_data/FIN/*')

print('[OK] Minion Data Cleared!')

