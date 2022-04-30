import envControlFuncs
import RPi.GPIO as GPIO
import time
import detect
import datetime

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
p.ChangeDutyCycle(75) # rpm

# get the saved token and chat ID after user starts the chat
with open ("savedToken.txt", "r") as myfile:
    savedToken = str(myfile.read().splitlines())
    
with open ("botChatID.txt", "r") as myfile:
    cid = str(myfile.read().splitlines())

savedToken = savedToken[2:-2]
cid = cid[2:-2]
cid = int(cid)

# create bot instance
bot = telebot.TeleBot(savedToken)


def fillTank():
    dt('tankTime.txt')
    # variable used for unit testing
    hasFilled = False
    
    GPIO.output(20,True)
    if envControlFuncs.waterTankDepth() > 0.3:
        while envControlFuncs.waterTankDepth() > 0.3:
            # 'False' turns the relay ON
            GPIO.output(20,False)
            hasFilled = True
        GPIO.output(20,True)
    
    return hasFilled
    
def irrigation():
    dt('irrigationTime.txt')
    # variable used for unit testing
    hasWatered = False
    
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
    dt('ventilationTime.txt')
    # variables used for unit testing
    hasOpened = False
    hasClosed = False
    
    interior, exterior = envControlFuncs.greenhouseTemp()
    if interior > exterior and interior > 25:
        while envControlFuncs.windowOpenDistance() < 1.8:
            # connect relay to allow for energising of the DC motor
            GPIO.output(26,False)
            # drive motor forwards
            GPIO.output(in1,GPIO.HIGH)
            GPIO.output(in2,GPIO.LOW)
            hasOpened = True
    elif exterior > interior and interior < 25:
        while envControlFuncs.swindowOpenDistance() > 1.5:
            GPIO.output(26,False)
            # drive motor backwards
            GPIO.output(in1,GPIO.LOW)
            GPIO.output(in2,GPIO.HIGH)
            hasClosed = True
    
    # turn off dc motor by opening relay terminal
    GPIO.output(26,True)
    return hasOpened, hasClosed

# save datetime of when environmental control function was last used
def dt(path):
    dt = str(datetime.datetime.now())
    # remove milliseconds
    for x in range(0, 7):
        dt = dt[:-1]
    # overwrite last saved datetime
    with open(path, "w") as myfile:
        myfile.write(dt)

while True:
    # fill tank after waiting period so that the air-water boundary is as still as possible
    fillTank()
    irrigation()
    ventilation()
    # if a weed is detected, let the user know!
    if detect.main() != "Nothing":
        bot.send_message(cid, "There is a weed in your greenhouse!")
        
    time.sleep(1800)

    
        