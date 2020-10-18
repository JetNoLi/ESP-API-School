import machine

#Note all functions will be called from main, i.e will be able to input the function in the
#callback thus no need to map to a function
#Callback statement can only have 1 param = to pin it is triggered on
def listen(pin, edge, callback):
    edge = int(edge)
    
    #edge = 0 -> trigger on falling edge
    if edge == 0:
        pin.irq(trigger = machine.Pin.IRQ_Falling, handler = callback)

    #edge = 1 -> trigger on rising edge
    elif edge == 1:                                          
        pin.irq(trigger = machine.Pin.IRQ_Rising, handler = callback)

    #edge = 10 -> trigger on either a rising or falling edge
    elif edge == 10:
        pin.irq(trigger = machine.Pin.IRQ_Falling | machine.Pin.IRQ_Rising, handler = callback) 

    else:
        print("Error: Incorrect input paramaters, edge must = 0, 1, 10")
    


#toggles the value of the pin
def switch(pin):

    if pin.value():
        pin.off()
    
    else:
        pin.on()



#schedule device to do function every x amount of milliseconds
#time is in milliseconds 
#params is params to pass into function
def timedInterrupt(pinNum, function, time, timerFunction):
    timer = machine.Timer(-1)           #initialize with ID of -1 as in docs

    timer.init(mode = machine.TIMER.PERIODIC, period = time, callback = timerFunction )

    return timer, pinNum, function


#end the timer i.e. deinitialize it
def endTimedInterrupt(timer):
    timer.deinit()
    #handle in main



#returns an ADC read of 
def ADC(pin):
    
    bitRead = pin.read()            #0-1024, 10 bit ADC 2^10 -1 = max = 1023, max = 1V
    
    voltage = (bitRead/1023.0)      #convert to analog reading 
    
    return voltage



#Note digital read will keep state device by use of text file mapping pin use
#def digital read
#digital read to save memory will be implemented directly in the callback code
    


