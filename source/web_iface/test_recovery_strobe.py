#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_hat import MinionHat
import time

# Create and instance of MinionHat()
minion_hat = MinionHat()

# Active Time in seconds
active_time_secs = 10

sys.stdout.write("Recovery Strobe Enabled")
sys.stdout.flush()
# minion_hat.strobe_timing(125, 1875)  # 125ms on, 1875ms off
minion_hat.strobe(minion_hat.ENABLE)

for idx in range(active_time_secs):
    time.sleep(1)
    sys.stdout.write(".")
    sys.stdout.flush()

# Disable the Recovery Strobe
print(" Recovery Strobe Disabled")
minion_hat.strobe(minion_hat.DISABLE)
