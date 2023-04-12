#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/pi/Documents/Minion_tools/')
from minion_toolbox import MinionToolbox

# create an instance of MinionToolbox()
minion_tools = MinionToolbox()

samp_time = minion_tools.update_timestamp()

samp_time = samp_time.split('_')

samp_date = samp_time[0]

samp_hour = samp_time[1]

samp_date = samp_date.replace('-', '/')

samp_hour = samp_hour.replace('-', ':')

samp_time = "{} {}".format(samp_date, samp_hour)

print("<fieldset><h3>")

print("Time:  {}<br>".format(samp_time))

print("<br>Sample counter: {}<br>".format(minion_tools.read_samp_num()))

print("</h3></fieldset>")
