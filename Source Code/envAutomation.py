import envControlFuncs
import RPi.GPIO as GPIO
import time

# set GPIO numbering mode and define output pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(20,GPIO.OUT) 
GPIO.setup(26,GPIO.OUT)
GPIO.setup(21,GPIO.OUT) 

# Relay HAT
GPIO.output(20,True) # solenoid valve
GPIO.output(26,True) # DC Motor
GPIO.output(21,True) # water pump

# L298N DC Motor Driver
in1 = 24
in2 = 23
en = 25
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
p=GPIO.PWM(en,1000)
p.ChangeDutyCycle(75)


def fillTank():
    hasFilled = False
    # Fill water tank
    GPIO.output(20,True)
    if envControlFuncs.waterTankDepth() > 0.3:
        while envControlFuncs.waterTankDepth() > 0.3:
            # 'False' turns the relay ON
            GPIO.output(20,False)
            hasFilled = True
        GPIO.output(20,True)
    
    return hasFilled
    
def irrigation():
    hasWatered = False
    # water crops
    if envControlFuncs.soilMoisture() == True:
        while envControlFuncs.soilMoisture == True: # and envControlFuncs.waterTankDepth < 0.7
            # 'False' turns the relay ON
            GPIO.output(21,False)
            hasWatered = True
        GPIO.output(21,True)
    else:
        GPIO.output(21,True)
        
    return hasWatered

def ventilation():
    hasOpened = False
    hasClosed = False
    interior, exterior = envControlFuncs.greenhouseTemp()
    if interior > exterior and interior > 25:
        while envControlFuncs.windowOpenDistance() < 1.8:
            GPIO.output(26,False)
            GPIO.output(in1,GPIO.HIGH)
            GPIO.output(in2,GPIO.LOW)
            hasOpened = True
    elif exterior > interior and interior < 25:
        while envControlFuncs.swindowOpenDistance() > 1.5:
            GPIO.output(26,False)
            GPIO.output(in1,GPIO.LOW)
            GPIO.output(in2,GPIO.HIGH)
            hasClosed = True
            
    GPIO.output(26,True)
    return hasOpened, hasClosed


while True:
    # fill tank after waiting period so that the air-water boundary is as still as possible
    fillTank()
    irrigation()
    ventilation()
    time.sleep(1800)

    
        