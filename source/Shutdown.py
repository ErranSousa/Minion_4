#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_hat import MinionHat

# Create and instance of MinionHat()
minion_hat = MinionHat()

# shutdown for a very long time...
num_years = 1
shutdown_secs = num_years * 8760 * 60

res = ''
while res not in {"y", "n"}:
    res = input("Confirm Shutdown? (Enter y/n)").lower()

if res == 'y':
    print('========================================================================')
    print('Permanent shutdown mode.\n  '
          'To wake the device, press the reset button or restart with the magnet.')
    print('========================================================================')
    # Turn on the LED controlled by the Minion Hat microcontroller.
    # Once this LED is turned off, the user can attach the magnet to keep the minion off.
    minion_hat.led(minion_hat.ON)
    minion_hat.shutdown(shutdown_secs)
else:
    print('Shutdown canceled.')






