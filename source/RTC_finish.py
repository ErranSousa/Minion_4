#!/usr/bin/env python3
import os

# Write deployment scripts to rc.local
os.system(
    "sudo sed -i '/# Print the IP/i# Synchronize the RPi Clock to the external RTC for every startup\n' /etc/rc.local")
os.system(
    "sudo sed -i '/# Print the IP/isudo python3 /home/pi/Documents/Minion_tools/RTC_sync_rpi.py\n\n' /etc/rc.local")
os.system(
    "sudo sed -i '/# Print the IP/i# Choose one of the following Handlers:\n' /etc/rc.local")
os.system(
    "sudo sed -i '/# Print the IP/isudo python3 /home/pi/Documents/Minion_scripts/Minion_DeploymentHandler.py &\n' /etc/rc.local")
os.system(
    "sudo sed -i '/# Print the IP/i#sudo python3 /home/pi/Documents/Minion_scripts/Gelcam_DeploymentHandler.py &\n' /etc/rc.local")

# Remove self from rc.local and configure deployment

# Open rc.local
with open('/etc/rc.local', 'r') as file:
    rclocal = file.read()

# Replace the RTC string
rclocal = rclocal.replace('sudo python3 /home/pi/Documents/Minion_tools/RTC_finish.py', '')

# Write the file out again
with open('/etc/rc.local', 'w') as file:
    file.write(rclocal)

os.system('sudo python /home/pi/Documents/Minion_tools/dhcp-switch.py')

os.system('sudo reboot now')

print("DONE!")
