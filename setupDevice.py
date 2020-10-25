brokerIP = input("Enter Broker IP Address: ")
brokerIP = "brokerIP = " + "\"" + brokerIP + "\"\n"

port = input("Broker Port Number: ")
port = "port = " + port + "\n"

ssid = input("SSID: ")
ssid = "ssid = " + "\"" + ssid + "\"\n"

psk = input("WiFi Password: ")
psk = "psk = " + "\"" + psk + "\"\n"

deviceName = input("Give your ESP a unique name: ")
deviceName = "deviceName = " + "\"" + deviceName + "\"\n"

pinCount = input("Number of Pins on ESP : ")
pinCount = "pinCount = " + pinCount + "\n"

SPIpins = input("Enter your 3 SPI pins seperated by a space: ")
SPIpins = SPIpins.split(" ")

SPIpins = "SPIPins = [" + SPIpins[0] + "," + SPIpins[1] + "," + SPIpins[2] + "]\n"

imports = ["import ubinascii\n","import machine\n"]
ClientID = "CLIENT_ID = ubinascii.hexlify(machine.unique_id())\n"
registered = "registered = 0\n"

print("Generating config file...")

with open("configTest.py","w") as conFile:
    conFile.writelines(imports)
    conFile.write("\n")
    conFile.write(brokerIP)
    conFile.write(port)
    conFile.write(ssid)
    conFile.write(psk)
    conFile.write(ClientID)
    conFile.write(deviceName)
    conFile.write(pinCount)
    conFile.write(SPIpins)
    conFile.write("\n")
    conFile.write(registered)

print("Complete")