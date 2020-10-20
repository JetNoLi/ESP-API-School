import config

def genPinFile():
    with open("pins.txt","w") as pinFile:

        for i in range(config.pinCount + 1):    #account for timer
            pinFile.write("")                   #note "-" indicates an unitialized pin
            pinFile.write("\n")

def getPinList():
    pins = []        #return list for pins 
    
    IOlist = []      #A = ADC, I = input, i = interrupt, O = output                           
    timer = None
    #functionDict = getFunctionMapDict()
    #functionList = getFunctionNames()
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
                if pinData == "" or pinData =="\n":
                    pins.append("")
                    IOlist.append("")

                elif (count + 1) == config.SPIPins[-1]:
                    pinData = pinData.split("_")
                    #print("here")
                    #SPISetup = functions.SetupSPI(int(pinData[0]),int(pinData[1]), int(pinData[2]))


            elif pinData == "\n":                 #unitialized pin
                pins.append("")
                IOlist.append("")
                print(count)

            # functionList:       #is ADC or digitalRead
                #pin = machine.Pin(count + 1,machine.Pin.IN)     #pinNum = index + 1

              ##  if pinData == "ADC":
                    #pin = machine.ADC(count+1)
                    #pins.append(pin)
                    #IOlist.append("A")
        
                #just configure as input for digitalRead
               ## else:
                   # pins.append(pin)
                    #IOlist.append("I")
                

            #could be a switch call in which case, just set to prior value as an output device
            #could be a listen call in which case schedule interrupt on pin
            else:
                if "_" in pinData:
                    pinData = pinData.split("_")                 #functionName_param1_param2...value

                    #variables used to set up the pin
                    #function = functionDict[pinData[0]]
                    #functionString = pinData[0]
                    
                    length = len(pinData)
                
                    if length == 2: #switch
                        #pin = machine.Pin(count + 1, machine.Pin.OUT, value = int(pinData[1]))                #count + 1 -> pinNum
                        #pins.append(pin)
                        IOlist.append("O")

                    else:           #interruput
                        #pin = machine.Pin(count + 1, machine.Pin)

                        #so if this doesnt trigger
                        #will return an interrupt list of input pins, ready to be handled
                        #usually this function is passed in main, this was an easy solution will test later

                        if pinData[1] == "1":      #was written to file so in string format 
                            
                            pin.irq(trigger = Pin.IRQ_RISING, handler = interruptCB)

                        if pinData[1] == "0":
                            pin.irq(trigger = Pin.IRQ_FALLING, handler = interruptCB)

                        else:
                            pin.irq(trigger = Pin.IRQ_RISNING | Pin.IRQ_FALLING, handler =interruptCB)
                    
                        pins.append(pin)
                        IOlist.append("i")

            count += 1

    return IOlist

IOlist = getPinList()

print(len(IOlist))