#!/usr/bin/env python
import os

import RPi.GPIO as GPIO

wifi = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(wifi, GPIO.OUT)
GPIO.output(wifi, 1)




# Write deployment scripts to rc.local
os.system(
    "sudo sed -i '/# Print the IP/i# Synchronize the RPi clock to the external RTC\n' /etc/rc.local")
os.system(
    "sudo sed -i '/# Print the IP/isudo python /home/pi/Documents/Minion_tools/RTC_sync_rpi.py\n' /etc/rc.local")
os.system(
    "sudo sed -i '/# Print the IP/i# Choose one of the following Handlers\n' /etc/rc.local")
os.system(
    "sudo sed -i '/# Print the IP/isudo python /home/pi/Documents/Minion_scripts/Minion_DeploymentHandler.py &\n' /etc/rc.local")
os.system(
    "sudo sed -i '/# Print the IP/i#sudo python /home/pi/Documents/Minion_scripts/Gelcam_DeploymentHandler.py &\n' /etc/rc.local")

# Remove self from rc.local and configure deployment

# Open rc.local
with open('/etc/rc.local', 'r') as file:
    rclocal = file.read()

# Replace the RTC string
rclocal = rclocal.replace('sudo python /home/pi/Documents/Minion_tools/RTC_finish.py', '')

# Write the file out again
with open('/etc/rc.local', 'w') as file:
    file.write(rclocal)

os.system('sudo python /home/pi/Documents/Minion_tools/dhcp-switch.py')

os.system('sudo reboot now')

print("DONE!")
