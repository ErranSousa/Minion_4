#!/usr/bin/env python

# Written to make switching wireless networks easier!
# Be careful, as you need to be in .Minion in order to retain your static IP

# import needed libraries for scanning and executing
import glob
import os
import time

# Filenames of interest
Minion = "dhcpcd.Minion"
internet = "dhcpcd.internet"
# Target Directory
os.chdir("/etc")
# List of dhcpcd.* files
files = []
# Scan for files
for file in glob.glob("dhcpcd.*"):
    files.append(file)

# If you wanna see the output
# print(files)

# Decide what to do with this information
# IF Else decision type
# Copy the .conf to the missing file and move the alt to .conf

if Minion in files:
    os.system('sudo cp /etc/dhcpcd.conf /etc/dhcpcd.internet')
    print("Copying .conf to .internet")
    os.system('sudo cp /etc/dhcpcd.Minion /etc/dhcpcd.conf')
    print("Copying .Minion to .conf")
    os.system('sudo rm -rf /etc/dhcpcd.Minion')
    print("Now you have Minions!")

elif internet in files:
    os.system('sudo cp /etc/dhcpcd.conf /etc/dhcpcd.Minion')
    print("Copying .conf to .Minion")
    os.system('sudo cp /etc/dhcpcd.internet /etc/dhcpcd.conf')
    print("Copying .internet to .conf")
    os.system('sudo rm -rf /etc/dhcpcd.internet')
    print("Now you have internet!")

# Cheeky response when things are bad
else:
    print("Things aren't right here... expect spies.")

time.sleep(1)
# Restart network interfaces for actions to take effect
os.system('sudo service dhcpcd restart')

print("Double plus good.")
