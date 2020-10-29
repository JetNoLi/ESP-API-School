#import test
import network
import functions
from machine import Pin
from machine import SPI
from machine import Timer
from machine import ADC
import config


def connectToWifi(ssid, psk):
    '''
    Connects to the WiFi ssid, using the psk

    param ssid: The ssid of the WiFi network to connect to
    type ssid: str
    param psk: The psk of the WiFi network to connect to
    type psk: str
    '''
    wlan = network.WLAN(network.STA_IF)         #create station mode
    wlan.active(True)                           #activate
    
    if not wlan.isconnected():                  #check if connected to a wlan already
        print("Trying to connect to Network")

        wlan.connect(ssid,psk)                  #attempt to connect

        while not wlan.isconnected():
            pass                                #wait until connection is established
    



#List of the names of the functions in API
def getFunctionNames():
    '''
    Used to get a list of function names from the functions.py file
    
    return: a list of function names from functions
    rtype: list
    '''
    return ["switch", "ADC", "listen", "digitalRead","timedInterrupt", "SPIRead"]




def getTopics(deviceName):  
    '''
    Returns the list of topics associated with the given deviceName

    param deviceName: Unique name given to the device by the user
    type deviceName: string

    return: list of topics associated with deviceName
    rtype: list
    '''
    
    functionNames = getFunctionNames()

    topics = []

    for function in functionNames:
        topic = deviceName + "_" + function     #topics take the form -> deviceName_function 
        topics.append(bytes(topic, 'UTF-8'))    #topics sent must be in bytes formate

    return topics


def getFunctionMapDict():
    '''
    Get the dictionary which maps function names to functions

    return: a dictionary which maps function names to functions
    rtype: dictionary
    '''
    return {"switch": functions.switch,
            "ADC": functions.ADC,
            "listen" : functions.listen,
            "digitalRead" : functions.digitalRead,
            "timedInterrupt" : functions.timedInterrupt,
            "SPIRead" : functions.SPIRead
            }


#get dictionary which maps topics to function
def getTopicDict(deviceName):
    '''
    Get a dictionary which maps topic names to functions

    param deviceName: The name of the device to get topics for
    type param: string

    return: a dictionary which maps topic names to functions
    rtype: dictionary
    '''
    topics = getTopics(deviceName)

    topicDict = {
        topics[0] : functions.switch,
        topics[1] : functions.ADC,
        topics[2] : functions.listen,
        topics[3] : functions.digitalRead,
        topics[4] : functions.timedInterrupt,
        topics[5] : functions.SPIRead
    }

    return topicDict




def isInput(functionName):
    '''
    Tells us if the given functionName is an input or output function

    param functionName: function to check if input or output
    type functionName: string

    return: True if input, False if output
    rtype: boolean
    '''
    functionNames = getFunctionNames()
    
    index = functionNames.index(functionName)       #find position

    if index < 2: 
        return False
    
    else:
        return True



#returns response topics already formated as bytes
def getResponseTopics():
    '''
    Get a list of topics to respond to the broker with

    return: a list of response topics
    rtype: list
    '''
    response = [b"addToDB"]           
    
    topic = "updateDB" + "_" + config.deviceName       #updateDB_deviceName

    response.append(bytes(topic,'UTF-8'))             #add in  bytes formate

    return response



def clientSubscribe(client):
    '''
    Subscribe to necessary topics to integrate use with API functions

    param client: MQTT client in main which handles sending and recieving messages
    type client: Client
    '''
    topics = getTopics(config.deviceName)

    for topic in topics:
        client.subscribe(topic)



#defualt file to generate i.e. All pins inactive
#text file eddited as follows
#line represents a pin number. i.e. pin 1, on line 1, index 0 etc. 
def genPinFile():
    with open("pins.txt","w") as pinFile:

        for i in range(config.pinCount + 1):    #account for timer
            pinFile.write("u")                   #note "" indicates an unitialized pin
            pinFile.write("\n")




def getPinList():
    '''
    Get the setup variables from reading the pinFile, pins, IOlist, timer, SPISetup

    return: a list of pins (type Pin) containing pin config from pin file
    rtype: list
    return: the input output list for the pins from the pin config from pin file
    rype: list
    return: data to create a timer from main. Is None if pin config has no timer
    rtype: Timer
    return: instance of the SPI class for the hardware SPI pins. Is None if pin config says no SPI setup
    rtype: SPI
    '''
    pins = []        #return list for pins 
    
    IOlist = []      #A = ADC, I = input, i = interrupt, O = output                           
    timer = None
    functionDict = getFunctionMapDict()
    functionList = getFunctionNames()
    SPISetup = None

    with open("pins.txt","r") as pinFile:
        pinRead = pinFile.readlines()
        count = 0                               #index in pinList 0-17         

        for pinData in pinRead:
            #print(count)
            #print(pinData)
    
            if count == config.pinCount:        #on Timer
                if pinData == "u":
                    pins.append("u")             #stores pin num to link to the timer
                    IOlist.append("u")
                
                elif pinData.strip("\n") == "u":
                    pins.append("u")
                    IOlist.append("u")

                else:
                    pinData = pinData.split("_")
                    timer = pinData
                    pins.append("t")
                    IOlist.append("t")


            elif pinData == "u":                 #unitialized pin
                pins.append("u")
                IOlist.append("u")
                #print("no newline")

            elif pinData.strip("\n") == "u":
                pins.append("u")
                IOlist.append("u")
                #print("newline")


            elif pinData in functionList:       #is ADC or digitalRead
                pin = Pin(count + 1,Pin.IN)     #pinNum = index + 1

                if pinData == "ADC":
                    pin = machine.ADC(count+1)
                    pins.append(pin)
                    IOlist.append("A")
        
                #just configure as input for digitalRead
                else:
                    pins.append(pin)
                    IOlist.append("I")
                

            #could be a switch call in which case, just set to prior value as an output device
            #could be a listen call in which case schedule interrupt on pin
            
            else:
                from main import interruptCB                    #Find workaround for Ed's code
                if "_" in pinData:
                    pinData = pinData.split("_")                 #functionName_param1_param2...value

                    #variables used to set up the pin
                    function = functionDict[pinData[0]]
                    functionString = pinData[0]
                    
                    length = len(pinData)
                
                    if length == 2: #switch
                        pin = Pin(count + 1, Pin.OUT, value = int(pinData[1]))                #count + 1 -> pinNum
                        pins.append(pin)
                        IOlist.append("O")
                    
                    elif pinData[0] == "SPI": #if an SPI Pin
                        IOlist.append("SPI")
                        pins.append("SPI")

                        pinData = pinData.split("_")
                        SPISetup = functions.SetupSPI(int(pinData[1]),int(pinData[2]), int(pinData[3]))

                    else:           #interruput
                        
                        pin = Pin(count + 1, Pin.IN)

                        #so if this doesnt trigger
                        #will return an interrupt list of input pins, ready to be handled
                        #usually this function is passed in main, this was an easy solution will test later

                        if pinData[1] == "1":      #was written to file so in string format 
                            
                            pin.irq(trigger = Pin.IRQ_RISING, handler = interruptCB)

                        if pinData[1] == "0":
                            pin.irq(trigger = Pin.IRQ_FALLING, handler = interruptCB)

                        else:
                            pin.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler =interruptCB)
                    
                        pins.append(pin)
                        IOlist.append("i")

            count += 1

    #len(pins)
    return pins, IOlist, timer, SPISetup
    
                

def writeToPinFile(pin,pinLine):
    '''
    given pin and string to write to file, will adjust line in pinFile accordingly to allow accurate startup

    param pin: pin number of the pin which is being changed, note pinCount + 1 = Timer line
    type pin: int
    param pinLine: line to write to pins.txt i.e.the pin file
    type pinLine: string
    '''
    pinLines = []

    #read from file and edit lines
    with open("pins.txt","r") as pinFile:
        pinRead = pinFile.readlines()

        for i in range(len(pinRead)):
            if pin == "SPI":
                if i in config.SPIPins:
                    pinLines.append(pinLine)

            elif i == pin - 1:                    #if line corresponds to pin, -1 to account for index
                pinLines.append(pinLine)        #edit line
            
            else:
                pinLines.append(pinRead[i])

    with open("pins.txt","w") as pinFile:
        for line in pinLines:
            pinFile.write(line)          




def getPinLine(message, topic, topics, value):
    '''
    Will generate the string to update the pinFile with i.e. pinLine

    param message: message recieved by MQTT client
    type message: string
    param topic: topic of the message recieved by the MQTT client
    type topic: string
    param topics: list of topics associated with the device
    type topics: list
    param value: value to add to pinLine if necessary, else enter -1
    type value: int

    return: get the pineLine to write to the pin file
    rtype: string
    '''
    pinLine = ""

    if  type(message) == type(topics):          #listen or timer or SPIRead
        #message = message.split("_")
        pinNum = message[0]
        
        #listen - pin, edge, callback
        if topic == topics[2]:  
            edge = message[1]
            function = message[2]
            pinLine = "listen_"+ edge + "_" + function
        
        #SPIRead - baudRate, CPOL, CPHA
        elif topic == topics[5]:
            pinLine = "SPI_" + message[0] + "_" + message[1] + "_" + message[2] 

        #timedInterrupt - pin, function, time, defualt value
        elif topic == topics[4]:
            print("here")
            function = message[1]
            time = message[2]
            pinLine = function + "_" + pinNum + "_" + time
    
    else:
        pinNum = message    #switch,ADC or digitalRead

        #switch
        if topic == topics[0]:     #convert to string as topic may be in bytes format
            #get pin value
            pinLine = "switch_" + str(value)
        
        #ADC
        if topic == topics[1]:
            pinLine = "ADC"
        
        #digitalRead
        if topic == topics[3]:
            pinLine = "digitalRead"

        #timer deinit
        if topic == topics[4]:
            pinLine = "u"

    pinLine += "\n"
    print("pinline = ",pinLine)
    return pinLine       




def formatSPIBytes(byteArray):
    '''
    Is the callback method to format SPI data to what you would like
    
    param byteArray: byte array taken in from reading the sensor
    paramType: list

    return: decoded sensor value
    rtype: string
    '''
    pass



def registerDevice(client):
    '''
    register device to Broker i.e. send device name to Pi
    update registered varaible in config file if device unregistered

    param client: MQTT client in main which is used to handle sending MQTT messages
    type client: Client
    '''
    if config.registered == 0:
        client.publish(b"registerDevice",bytes(config.deviceName,'UTF-8'))
        print("published")
        configLines = []
        with open("config.py","r") as file:
            fileLines = file.readlines()

            for line in fileLines:
                if "registered" in line:
                    configLines.append("registered = 1")
                
                else:
                    configLines.append(line)
        
        with open("config.py","w") as writeFile:
            for line in configLines:
                writeFile.write(line)
    
    else: 
        print("Already Registered")



#returns the topic and the message to send to the broker
def updateDB(client, message, value,topic, topics):
    '''
    Generates the response message to send to update the Broker so it can update the Database

    param client: MQTT client in main which is used to handle sending MQTT messages
    type client: Client
    param message: message recieved by MQTT client
    type message: string
    param value: value to add to updateDB with.
    type value: string
    param topic: topic of the message recieved by the MQTT client
    type topic: string
    param topics: list of topics associated with the device
    type topics: list
    '''
    updateMessage = ""

    if topic == topics[0]:          #switch
        #message = pinNum
        updateMessage = config.deviceName + "_switch_" + message + "_" + value
    
    if topic == topics[1]:          #ADC
        #message = pinNum
        updateMessage = config.deviceName + "_ADC_" + message + "_" + value
    
    if topic == topics[2]:          #listen
        #message = pinNum, edge, listenCB | note value = edge
        print(message[0])
        updateMessage = config.deviceName + "_listen_" + message[0] + "_" + message[1]
    
    if topic == topics[3]:          #digitalRead
        #message = pinNum
        updateMessage = config.deviceName + "_digitalRead_" + message + "_" + value

    if topic == topics[4]:          #timer - note negative one to indicate not attached to a pin
        if message == "endTimer":
            updateMessage = config.deviceName + "_timedInterrupt_ended"
        
        else:
            #message[2] = time in milliseconds for timer to schedule interrupt
            updateMessage = config.deviceName + "_timedInterrupt_-1_" + message[2]
    
    if topic == topics[5]:
        if "_" not in message:                   
            updateMessage = config.deviceName + "_SPIRead_" + str(config.SPIPins[0]) + value
        
        else:
            updateMessage = config.deviceName + "_SPIRead_" + str(config.SPIPins[0]) + value
            
    client.publish(b"updateDB", bytes(updateMessage,'UTF-8'))

