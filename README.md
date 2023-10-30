
# Minion 4 Install Instructions

### Prepare a fresh install of raspbian on micro-sd card:

&emsp; https://www.raspberrypi.org/software/

&emsp; It is highly recommended to use the Raspberry Pi Imager

&emsp; Currently, only the Raspian Buster OS is supported by Minion 4

### Power Pi via micro-USB

&emsp;At this stage you should have:

- SD card in Pi
- Wired LAN
- Keyboard/Mouse
- Monitor
- No Minion 4 HAT

### Follow on screen instructions

&emsp;Install raspbian Buster as normal

&emsp;Choose any password for the device

&emsp;Skip wireless setup

&emsp;When prompted, update the computer - this may take a while

&emsp;Allow the Raspberry Pi to reboot

### Clone Repo and Install

&emsp;Once the Pi reboots, open a terminal and type this command to download the repo:


  `~$ sudo git clone https://github.com/ErranSousa/Minion_4.git`
  
&emsp;Now navigate into the folder and begin the install process:
  
  `~$ cd Minion_4/`
  
  `~/Minion/$ sudo python Minion_install.py`
  
  &emsp;Assign the device with an IP address between 2 and 250
  
  &emsp;Enter [Y] to enable debug mode
  
  &emsp;Enter [N] to choose to have files saved to the Desktop
  
  &emsp;Allow the installer to finish and it will turn the Pi off
  
  &emsp;Disconnect USB power from the Pi
  
  &emsp;Finally power on the Minion_Hub and Master_Hub
  
  ### Attach HAT and power with 9-12V through the power connector  
  
  &emsp;The Pi will boot up and complete it's installation (setting the clock)
  
  &emsp;Then the Pi will reboot
  
  &emsp;Once the Pi reboots you may disconnect the LAN network cable
  
  ### Test if the Minion is working
  
  &emsp;Connect to the Minion_Hub with your cell phone or another computer:
  
  &emsp;Open a brouser and type the IP of the Minion
  
  &emsp;(i.e. 192.168.0.XXX)
  
  &emsp;If you are greeted with a website then you did it!
  
  
  
  
  
