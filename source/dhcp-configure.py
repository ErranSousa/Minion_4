# Written to make switching wireless networks easier!
# Be careful, as you need to be in .Minion in order to retain your static IP

# Here we will ensure the Minion is using its local IP once it is connected to the Hub

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

# Display the list of file
# print(files)

# Decide what to do with this information

# Copy the .conf to the missing file and move the alt to .conf

if Minion in files:
	os.system('sudo cp /etc/dhcpcd.conf /etc/dhcpcd.internet')
	print("Copying .conf to .internet")
	os.system('sudo cp /etc/dhcpcd.Minion /etc/dhcpcd.conf')
	print("Copying .Minion to .conf")
	os.system('sudo rm -rf /etc/dhcpcd.Minion')
	print("Now you have Minion_Hub!")

elif internet in files:
	print("You are alread on the Minion Network!")

# Cheeky response when things are bad
else:
	print("Bro you messed it up...")

time.sleep(1)
# Restart network interfaces for actions to take effect
os.system('sudo service dhcpcd restart')

print("Double plug good")
