from machine import Pin
from machine import Timer
from machine import SPI
import APIUtils as Utils

#Note all functions will be called from main, i.e will be able to input the function in the
#callback thus no need to map to a function
#Callback statement can only have 1 param = to pin it is triggered on

def listen(pin, edge, callback):
    '''
    Triggers an interrupt on the given pin

    param pin: pin configured as input which interrupt will be called on
    type pin: Pin
    param edge: edge which interrupt will be called on. 0 - Falling, 1 - Rising, 10 - either
    type edge: string
    param callback: function to call when interrupt triggers
    type callback: function
    '''
    edge = int(edge)
    
    #edge = 0 -> trigger on falling edge
    if edge == 0:
        pin.irq(trigger = Pin.IRQ_FALLING, handler = callback)

    #edge = 1 -> trigger on rising edge
    elif edge == 1:                                          
        pin.irq(trigger = Pin.IRQ_RISING, handler = callback)

    #edge = 10 -> trigger on either a rising or falling edge
    elif edge == 10:
        pin.irq(trigger = Pin.IRQ_FALLING | Pin.IRQ_RISING, handler = callback) 

    else:
        print("Error: Incorrect input paramaters, edge must = 0, 1, 10")
    



def switch(pin):
    '''
    toggles the value of the pin

    param pin: The pin, which has been configured as an output, to toggle
    type pin: Pin
    '''
    if pin.value():
        pin.off()
    
    else:
        pin.on()



#schedule device to do function every x amount of milliseconds
#time is in milliseconds 
#params is params to pass into function
def timedInterrupt(pinNum, function, time, timerFunction):
    '''
    Function which creates a timer to schedule tasks

    param pinNum: pinNum of the pin to trigger function on
    type pinNum: int
    param function: Callback function which takes pinNum as param
    type function: function
    param time: time in milliseconds
    type time: string
    param timerFunction: timerCB, defualt value
    type timerFunction: function

    return: timer which stores the instance of Timer
    rtype: timer
    return: pinNum which was inputted
    rtype:int
    return: function which was inputted
    rtype: function
    '''
    timer = Timer(-1)           #initialize with ID of -1 as in docs
    timer.init(mode = Timer.PERIODIC, period = int(time), callback = timerFunction)

    return timer, pinNum, function



#end the timer i.e. deinitialize it
def endTimedInterrupt(timer):
    '''
    End the already existing Timer

    param timer: is the Timer instance to end
    timer type: Timer
    '''
    timer.deinit()
    timer = None
    #handle in main, update IOlist, timerFunction, pins final index stores timer Pin Number



#returns an ADC read of 
def ADC(pin):
    '''
    Reads an analog value from the pin configured for ADC
    
    param pin: pin to read from
    pin type: Pin

    return: The voltage reading from the pin, note max voltage = 1V
    rtype: float
    '''
    
    bitRead = pin.read()            #0-1024, 10 bit ADC 2^10 -1 = max = 1023, max = 1V
    
    voltage = (bitRead/1023.0)      #convert to analog reading 
    
    return voltage



def digitalRead(pin):
    '''
    Read whether the specified pin is a high or low

    param pin: pin to read from
    pin type: Pin

    return: 1 if a High, 0 if low
    rtype: int
    '''
    return pin.value()



#Returns an instance of the SPI class which will be loaded in the main
def SetupSPI(baudRate, CPOL, CPHA): 
    '''
    Setup an instance of the SPI class

    param baudRate: baudRate for SPI reading
    type baudRate: int
    param CPOL: clock polarity in accordance with SPI CPOL
    type CPOL: int
    param CPHA: clock phase in accordance with SPI CPHA
    type CPHA: int

    return: an instance of the SPI type, in accordance with paramaters
    rtype: SPI
    '''
    #default pins MISO - GPIO12, MOSI - GPIO13, SCLK - GPIO14
    return SPI(1, baudrate = baudRate, polarity = CPOL, phase = CPHA)



def SPIReadValue(byteSize, SPISetup):
    '''
    Read the given number of bytes from the setup SPI

    param byteSize: number of bytes to read
    type byteSize: int
    param SPISetup: configured instance of SPI class
    type SPISetup: SPI

    return: Value read by SPI
    rtype: string
    ''' 
    buffer = bytearray(byteSize)    #stores bits read in as they have to be in bytes format
    SPISetup.readinto(buffer)

    return Utils.formatSPIBytes(buffer)


 
def SPIRead(baudRate, CPOL, CPHA, byteSize, SPISetup):
    '''
    Create SPIRead if necessary, write to scheduled SPI pins in pin File
    To just read use format (0,0,0, byteSize, SPISetup)
    Cannot set SPI from callback, only read from it

    param baudRate: baudRate for SPI reading
    type baudRate: int
    param CPOL: clock polarity in accordance with SPI CPOL
    type CPOL: int
    param CPHA: clock phase in accordance with SPI CPHA
    type CPHA: int
    param byteSize: number of bytes to read
    type byteSize: int
    param SPISetup: configured instance of SPI class
    type SPISetup: SPI

    return: Value read by SPI
    rtype: string
    ''' 

    if SPISetup == None:
        SPISetup = SetupSPI(baudRate,CPOL,CPHA)
    
    return SPIReadValue(int(byteSize),SPISetup)
