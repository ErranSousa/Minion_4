import minsat
from minsat import MinSat

ex_msg = "Configure the Iridium 9602 Modem"

print("-"*len(ex_msg))
print(ex_msg)
print("-"*len(ex_msg))

gps_port = "/dev/ttySC0"
gps_baud = 9600
modem_port = "/dev/ttySC1"
modem_baud = 19200

m1 = MinSat(gps_port, gps_baud, modem_port, modem_baud)

print("Configuring the Modem")
m1.config_modem()
print("Complete")

