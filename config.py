import ubinascii
import machine 

#setup Variables
brokerIP = "192.168.1.40"
port = 8883
psk = "wirelesswifi@"
ssid = "Critical"
deviceName = "ESP-Li"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
pinCount = 18
SPIPins = [12,13,14,15] # list of dedicated SPI pins, -1 to account for index

#API variables
registered = 0
