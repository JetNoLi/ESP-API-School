import subprocess
import time

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
pins = int(pinCount)
pinCount = "pinCount = " + pinCount + "\n"

SPIpins = input("Enter your 4 SPI pins seperated by a space: ")
SPIpins = SPIpins.split(" ")

SPIpins = "SPIPins = [" + SPIpins[0] + "," + SPIpins[1] + "," + SPIpins[2] + "," + SPIpins[3] +"]\n"

imports = ["import ubinascii\n","import machine\n"]
ClientID = "CLIENT_ID = ubinascii.hexlify(machine.unique_id())\n"
registered = "registered = 0\n"

print("Generating config and pins file...")

with open("config.py","w") as conFile:
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


#defualt file to generate i.e. All pins inactive
#text file edited as follows
#line represents a pin number. i.e. pin 1, on line 1, index 0 etc. 

with open("pins.txt","w") as pinFile:

    for i in range(int(pins) + 1):    #account for timer
        pinFile.write("u")                   
        pinFile.write("\n")


print("Complete")

git = input("Would you like to download device files? (Y/N): ")
git = git.upper()

if git == "Y":
    subprocess.run(["git","clone","https://github.com/JetNoLi/ESP-DeviceFiles.git"])

linux = input("Are you on a linux device? (Y/N): ")
linux = linux.upper()

if linux == "N":
    print("Unfortunately amby is not supported on your current system")
    print("You will have to flash and copy the device files manually")

else:
    flash = input("Is your device flashed? (Y/N): ")
    
    if flash == "N":
        print("esptool.py is needed, use:")
        print("pip3 install esptool")
        time.sleep(1)

        serialPort = input("What is the serial port: ")

        print("Erasing Flash")
        subprocess.run(["esptool.py","--port",serialPort,"erase_flash"])
        print("Flash succesfuly ereased")

        toFlash = input("What is the micropython filepath: ")
        subprocess.run(["esptool.py","--port",serialPort,"--baud","115200","write_flash", "--flash_size=detect","0",toFlash])

    ampy = input("Is ampy installed on your system? (Y/N): ")
    
    if ampy =="N":
        subprocess.run(["sudo","apt-get","install","ampy"])
    
    else:
        serialPort = input("Serial Port Name: ")
        preAmble = "ESP-DeviceFiles/"
        fileNames = ["main.py","APIUtils.py","functions.py","simple2.py"]
        generatedFiles = ["pins.txt","config.py"]

        for fileName in fileNames:
            toCopy = preAmble + fileName 
            print("Copying ",fileName,"...")
            subprocess.run(["ampy","--port", serialPort, "put", toCopy])
            print("Copied")

        for fileName in generatedFiles:
            print("Copying ",fileName,"...")
            subprocess.run(["ampy","--port", serialPort, "put", fileName])
            print("Copied")
            

print("Finished Device Setup")