import network
import functions
import machine
import config
from main import interruptCB

def connectToWifi(ssid, psk):

    wlan = network.WLAN(network.STA_IF)         #create station mode
    wlan.active(True)                           #activate
    
    if not wlan.isconnected():                  #check if connected to a wlan already
        print("Trying to connect to Network")

        wlan.connect(ssid,psk)                  #attempt to connect

        while not wlan.isconnected():
            pass                                #wait until connection is established
    
    print("Connected to", ssid)



#List of the names of the functions in API
def getFunctionNames():
    return ["switch", "ADC", "listen", "digitalRead","timedInterrupt", "SPIRead"]



#returns the list of topics associated with the given deviceName
def getTopics(deviceName):  
    functionNames = getFunctionNames()

    topics = []

    for function in functionNames:
        topic = deviceName + "_" + function     #topics take the form -> deviceName_function 
        topics.append(bytes(topic, 'UTF-8'))    #topics sent must be in bytes formate

    return topics


def getFunctionMapDict():
    return {"switch": functions.switch,
            "ADC": functions.ADC,
            "listen" : functions.listen,
            "digitalRead" : functions.digitalRead,
            "timedInterrupt" : functions.timedInterrupt,
            "SPIRead" : functions.SPIRead
            }


#get dictionary which maps topics to function
def getTopicDict(deviceName):
    topics = getTopics(deviceName)

    topicDict = {
        topics[0] : functions.switch,
        topics[1] : functions.ADC,
        topics[2] : functions.listen,
        topics[3] : functions.digitalRead,
        topics[4] : functions.timedInterrupt,
    }

    return topicDict



#tells us if a function is an input or output function
def isInput(functionName):
    #index < 2 -> output, else input
    functionNames = getFunctionNames()
    
    index = functionNames.index(functionName)       #find position

    if index < 2: 
        return False
    
    else:
        return True



#returns response topics already formated as bytes
def getResponseTopics():
    response = [b"addToDB"]           
    
    topic = "updateDB" + "_" + config.deviceName       #updateDB_deviceName

    response.append(bytes(topic,'UTF-8'))             #add in  bytes formate

    return response


#client taken in is subscribed to all the API topics
def clientSubscribe(client,deviceName):
    #Subscribe to necessary topics to integrate use with API
    topics = getTopics(deviceName)

    for topic in topics:
        client.subscribe(topic)



#defualt file to generate i.e. All pins inactive
#text file eddited as follows
#line represents a pin number. i.e. pin 1, on line 1, index 0 etc. 
def genPinFile():
    with open("pins.txt","w") as pinFile:

        for i in range(config.pinCount + 1):    #account for timer
            pinFile.write("")                   #note "-" indicates an unitialized pin
            pinFile.write("\n")



#returns an array of pins (type Pin) and an IOlist which maps index to input output
#also returns a timer if their is one
#initalizes them according to the pins.txt file
#note we pass in the topicsDict instead of recreating it to save memory 
def getPinList():
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
    
            if count == config.pinCount:        #on Timer
                if pinData == "":
                    pins.append("")             #stores pin num to link to the timer

                else:
                    pinData = pinData.split("_")
                    timer = pinData

            elif (count + 1) in config.SPIPins: #if an SPI Pin
                if (count + 1) == config.SPIPins[-1]:
                    pinData = pinData.split("_")
                    SPISetup = functions.SetupSPI(int(pinData[0]),int(pinData[1]), int(pinData[2]))


            elif pinData == "":                 #unitialized pin
                pins.append("")
                IOlist.append("")

            elif pinData in functionList:       #is ADC or digitalRead
                pin = machine.Pin(count + 1,machine.Pin.IN)     #pinNum = index + 1

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
                if "_" in pinData:
                    pinData = pinData.split("_")                 #functionName_param1_param2...value

                    #variables used to set up the pin
                    function = functionDict[pinData[0]]
                    functionString = pinData[0]
                    
                    length = len(pinData)
                
                    if length == 2: #switch
                        pin = machine.Pin(count + 1, machine.Pin.OUT, value = int(pinData[1]))                #count + 1 -> pinNum
                        pins.append(pin)
                        IOlist.append("O")

                    else:           #interruput
                        pin = machine.Pin(count + 1, machine.Pin)

                        #so if this doesnt trigger
                        #will return an interrupt list of input pins, ready to be handled
                        #usually this function is passed in main, this was an easy solution will test later

                        if pinData[1] == "1":      #was written to file so in string format 
                            
                            pin.irq(trigger = machine.Pin.IRQ_RISING, handler = interruptCB)

                        if pinData[1] == "0":
                            pin.irq(trigger = machine.Pin.IRQ_FALLING, handler = interruptCB)

                        else:
                            pin.irq(trigger = machine.Pin.IRQ_RISNING | machine.Pin.IRQ_FALLING, handler =interruptCB)
                    
                        pins.append(pin)
                        IOlist.append("i")

            count += 1

    return pins, IOlist, timer, SPISetup
    
                

#given pin and string to write to file, will adjust line in pinFile accordingly to allow accurate startup
def writeToPinFile(pin,pinLine):
    pinLines = []

    #read from file and edit lines
    with open("pins.txt","r") as pinFile:
        pinRead = pinFile.readlines()

        for i in range(len(pinRead)):
            if i == pin - 1:                    #if line corresponds to pin, -1 to account for index
                pinLines.append(pinLine)        #edit line
            
            else:
                pinLines.append(pinRead[i])

    with open("pins.txt","w") as pinFile:
        pinFile.writelines(pinLines)            



#given the message and topic will generate the string to update the pinFile with i.e. pinLine
def getPinLine(pins, message, topic, topics):
    pinLine = ""

    if "_" in message:          #listen or timer or SPIRead
        message = message.split("_")
        pinNum = message[0]
        
        #listen - pin, edge, callback
        if topic == str(topics[2]):  
            edge = message[1]
            function = message[2]
            pinLine = "listen_"+ edge + "_" + function
        
        #SPIRead - baudRate, CPOL, CPHA
        elif topic == str(topics[4]):
            pinLine = "SPIRead_" + message[0] + "_" + message[1] + "_" + message[2] 

        #timedInterrupt - pin, function, time, defualt value
        else:
            function = message[1]
            time = message[2]
            pinLine = function + "_" + pinNum + "_" + time
    
    else:
        pinNum = message    #switch,ADC or digitalRead

        #switch
        if topic == str(topics[0]):     #convert to string as topic may be in bytes format
            #get pin value
            pinValue = pins[int(pinNum)-1].value()
            pinLine = "switch_" + str(pinValue)
        
        #ADC
        if topic == str(topics[1]):
            pinLine = "ADC"
        
        #digitalRead
        if topic == str(topics[1]):
            pinLine = "digitalRead"

    return pinLine       



#takes in byte value from sensor
#is the callback method to format SPI data to what you would like
def formatSPIBytes(byteArray):
    pass


#when a device is first used it will need to register with thebroker
def addToDB(IP, port):
    #register device to Broker i.e. send message to notify Pi to update DB, hence send on topic only Pi, is subscribed to 
    pass


#method which takes in the message recieved and the topic it was called on to
#returns the topic and the message to send to the broker
def updateDB(client, message, topic):
    pass