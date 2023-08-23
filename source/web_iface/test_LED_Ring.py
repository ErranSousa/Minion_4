#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox
import time

# Create an instance of MinionToolbox()
minion_tools = MinionToolbox()

GPIO, pin_defs_dict = minion_tools.config_gpio()

# Active Time in seconds
active_time_secs = 10

# Enable the LED Ring
sys.stdout.write("LED Ring Enabled")
sys.stdout.flush()
GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.HIGH)

for idx in range(active_time_secs):
    time.sleep(1)
    sys.stdout.write(".")
    sys.stdout.flush()

# Disable the LED Ring
GPIO.output(pin_defs_dict['LED_RING_CTRL'], GPIO.LOW)
print(" LED Ring Disabled")
