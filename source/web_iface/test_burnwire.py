#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_hat import MinionHat
import time

# Create and instance of MinionHat()
minion_hat = MinionHat()

# Burn Wire Active Time in seconds
active_time_secs = 10

# Enable the burn wire
sys.stdout.write("Burn Wire Enabled")
sys.stdout.flush()
minion_hat.burn_wire(minion_hat.ENABLE)

for idx in range(active_time_secs):
    time.sleep(1)
    sys.stdout.write(".")
    sys.stdout.flush()

# Disable the burn wire
print(" Burn Wire Disabled")
minion_hat.burn_wire(minion_hat.DISABLE)
