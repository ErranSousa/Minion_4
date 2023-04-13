#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_hat import MinionHat

# Create and instance of MinionHat()
minion_hat = MinionHat()

print('Goodbye')

# Turn on the LED controlled by the Minion Hat microcontroller.
# Once this LED is turned off, the user can attach the magnet to keep the minion off.
minion_hat.led(minion_hat.ON)

# Shutdown the minion for 60 seconds,  this should be enough time to get the magnet on.
# After 60 seconds, the minion will restart.  This is a fail-safe method to ensure that we do not accidentally
# enter sleep forever.
minion_hat.shutdown(60)


