import ubinascii
from machine import Pin
from machine import ADC
import machine
import APIUtils as Utils
import time
import config
import functions
from simple2 import MQTTClient

#for callbacks, pins do not need to be instantiated before hand
def switchCB(pinNum):
    global pins
    global client

    #execute function
    if IOlist[pinNum-1] == "O":

        if pins[pinNum-1].value == 0:
            pins[pinNum-1].on()

        else:
            pins[pinNum-1].off()
        
    else:
        pins[pinNum-1] = machine.Pin(pinNum, machine.Pin.OUT, value = 1)
        IOlist[pinNum-1] = "O"
    
    
    #updatePinsFile
    #updateBroker


def ADC_CB(pinNum):
    global pins
    global client
    
    voltage = -1

    if IOlist[pinNum-1] == "A":
        value = pins[pinNum-1].read()
        voltage = value/1023.0

    else:
        IOlist[pinNum-1] = "A"
        pins[pinNum-1] = machine.ADC(pinNum)
        value = pins[pinNum-1].read()
        voltage = value/1023.0
    
    #update pinsFile
    #update Broker


def digitalReadCB(pinNum):
    global pins
    global client

    value = -1

    if IOlist[pinNum-1] == "I" or IOlist[pinNum-1] == "O": 
        value = pins[pinNum-1].value()
    
    else:
        pins[pinNum-1] = machine.Pin(pinNum, machine.Pin.IN)
        value = pins[pinNum-1].value()
    
    #update pins file
    #update broker


def SPIReadCB(byteSize):
    global SPISetup

    functions.SPIRead(0,0,0,byteSize,SPISetup)

    #update pins file
    #update broker


#assume pin is already initialized
#redirect to callback above
#is a workaround as you cannot have params in the timer callback
def timerCB():
    timerFunction(pins[config.pinCount])


def interruptCB(pinNum):
    global client
    print("Button Pushed")
    #at the moment notifies the DB but can be edited to interrupt function of users choice
    #will run the updateDB method here
    pass




def getCallbackFunctions():
    return {"switchCB": switchCB,
            "ADC_CB": ADC_CB, 
            "digitalReadCB": digitalReadCB,
            "timerCB" : timerCB
            }


# Try to connect to Wifi - LED turns on and off
Utils.connectToWifi(config.ssid,config.psk)

# Config to connect to broker and handle API implementation
broker = config.brokerIP
CLIENT_ID = ubinascii.hexlify(machine.unique_id())

#stores client to allow to publish from subscriber callbacks
client = None

#to match topic to API call
topics = Utils.getTopics(config.deviceName)             #generates list of topics for given device     
topicDict = Utils.getTopicDict(config.deviceName)       #dictionary mapping topics to API functions
callbackMap = getCallbackFunctions()

#to store pin instances and then a list of their states, also attaches a timer if one was created
pins, IOlist, timerValue, SPISetup = Utils.getPinList()           #reads from the pin.txt file and reloads last state for each pin

timer = None
timerFunction = False       #stores the CB method for timer


#timerValue in the form functionName for CB, pinNum
if len(timerValue) == 3:
    #must still map callback to pin and init pin

    timer, pinNum, func = functions.timedInterrupt(timerValue[1], timerValue[0], timerValue[2], timerCB)
    pins[config.pinCount] = pinNum
    timerFunction = callbackMap[func]


#THIS IS WHAT HAPPENS WHEN STATE CHANGES CHANGE HERE TO IMPLEMENT FUNCTIONALITY
def sub_cb(topic, msg, r, d):
    global pins
    global IOlist
    global client
    global timer
    global timerFunction
    global SPISetup

    function = topicDict[topic]             #get function from dictionary

    #switch function input param is the pin
    if topic == topics[0]:                  #switch
        print(msg)
        pinNum = int(msg)

        if IOlist[pinNum-1] == "O":
            function(pins[pinNum-1])        #execute switch statement
        
        #reconfigure pins to output and set to high, as the first switch will always be an on
        else:
            pins[pinNum-1] = Pin(pinNum, Pin.OUT, value =1)
            IOlist[pinNum-1] = "O"

        #updateDB and pins.txt

            
    if topic == topics[1]:                  #ADC
        pinNum = int(str(msg))
        value = -1                          

        if IOlist[pinNum-1] == "A":
            value = function(pins[pinNum-1])        #execute ADC read statement
        
        #reconfigure pins to output and set to high, as the first switch will always be an on
        else:
            pins[pinNum-1] = ADC(pinNum)
            value = function(pins[pinNum-1])
            IOlist[pinNum-1] = "A"

    
    #updateDB and pins.txt

    if topic == topics[2]:                  #listen
        message = msg.decode('utf-8')
        message = message.split("_")
        print(message[0])
        pinNum = int(message[0])

        if IOlist[pinNum -1] == "I" or IOlist[pinNum-1] == "i":
            function(pins[pinNum-1],message[1],interruptCB)
            IOlist[pinNum] = "i"

        #set up as input
        else:
            pins[pinNum-1] = machine.Pin(pinNum, machine.Pin.IN)
            function(pins[pinNum-1], message[1], interruptCB)
            IOlist[pinNum] = "i"

        #updateDB and pins.txt


    if topic == topics[3]:                  #digitalRead
        pinNum = int(msg)
        value = -1

        if IOlist[pinNum-1] == "I":
            value = function(pins[pinNum-1])        #execute read
        
        #reconfigure pins to output and set to high, as the first switch will always be an on
        else:
            pins[pinNum-1] = machine.Pin(pinNum, machine.Pin.IN)
            IOlist[pinNum -1] = "I"        
            value = function(pins[pinNum-1])
            
        print(value)                #TRACING


    if topic == topics[4]:                  #timedInterrupt add if message = deInit
        if "_" in msg:

            message = msg.split("_")
            pinNum = int(message[0])

            timer, pinNum, func = function(pinNum, message[1], message[2], timerCB)

            pins[config.pinCount] = pinNum
            timerFunction = callbackMap[func]

        else:                               #deinit the timer
            if msg == "endTimer":
                functions.endTimedInterrupt(timer)
                timerFunction = None
                pins[config.pinCount] = ""


    #update pinFile and Broker

    if topic == topics[5]:                  #SPIRead
        if len(msg) == 1:                   #no Setup
            function(0,0,0,msg,SPISetup)
        
        else:
            message = msg.split("_")
            function(int(message[0]),int(message[1]), int(message[2]), message[3],SPISetup)
    
    #update PinFile and Broker






def main(server=broker):
    global client

    #Create Subscriber
    client = MQTTClient(CLIENT_ID, server)

    # Subscribed messages will be delivered to this callback
    client.set_callback(sub_cb)
    #connect to broker
    client.connect()

    #client.subscribe(TOPIC)
    Utils.clientSubscribe(client, config.deviceName)
    print("Subscribed")

    try: 
        while True:
            client.wait_msg()
        
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()

