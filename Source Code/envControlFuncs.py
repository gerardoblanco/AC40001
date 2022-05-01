import time
from w1thermsensor import W1ThermSensor
from gpiozero import DistanceSensor
import RPi.GPIO as GPIO
import sys

def waterTankDepth():
    # check water tank depth
    sensor = DistanceSensor(echo=13, trigger=19)
    depth = sensor.distance
    
    return depth
    
    
def greenhouseTemp():
    # check greenhouse internal and external temp
    sensor = W1ThermSensor()
    x = 0
    for sensor in W1ThermSensor.get_available_sensors():
        if x == 0:
            interior = sensor.get_temperature()
            x += 1
        else:
            exterior = sensor.get_temperature()
    
    return interior, exterior
    
def windowOpenDistance():
    sensor = DistanceSensor(6, 5)
    distance = sensor.distance
    
    return distance

def soilMoisture():
    #GPIO setup -- pin 29 as moisture sensor input
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12,GPIO.IN)
    if (GPIO.input(12))==0:
        dry = False
    elif (GPIO.input(12))==1:
        dry = True
    
    return dry

    
