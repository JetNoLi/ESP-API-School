import ubinascii
import machine 

#setup Variables
brokerIP = "192.168.1.40"
port = "8883"
ssid = "wirelesswifi@"
psk = "Critical"
deviceName = "ESP-Li"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
pinCount = 18
SPIPins = [12,13,14] # list of dedicated SPI pins, -1 to account for index

#API variables



