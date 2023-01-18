#!/usr/bin/env python3

# This script should be used to manually set the external DS3231 RTCC
# It also sychronizes the RPI time to the new time

import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

# create an instance of MinionToolbox()
minion_tools = MinionToolbox()

# Set the external DS3231 RTC Manually and automatically synchronize the RPi time.
minion_tools.rtc_ext_set_time(sync=True)
