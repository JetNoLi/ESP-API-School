#from simple2 import MQTTClient
import config 

def genPinFile():
    with open("pins.txt","w") as pinFile:

        for i in range(config.pinCount + 1):    #account for timer
            pinFile.write("")                   #note "" indicates an unitialized pin
            pinFile.write("\n")

genPinFile()