#from simple2 import MQTTClient
#import config 

def genPinFile():
    with open("pins.txt","w") as pinFile:

        for i in range(18 + 1):    #account for timer
            pinFile.write("u")                   #note "" indicates an unitialized pin
            pinFile.write("\n")

genPinFile()