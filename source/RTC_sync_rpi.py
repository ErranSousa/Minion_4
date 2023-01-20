#!/usr/bin/env python3

# This script should be used to set the Raspberry Pi Time based on the DS3231
# It also sychronizes the RPI time to the new time

import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

# create an instance of MinionToolbox()
minion_tools = MinionToolbox()

# Synchronize the Raspberry Pi time to the DS3231 RTC.
minion_tools.rtc_ext_sync_rpi()

print("[OK] Raspberry Pi Synchronized  to the DS3231")
