import time
from w1thermsensor import W1ThermSensor

sensor = W1ThermSensor()

while True:
    for sensor in W1ThermSensor.get_available_sensors():
        print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))

    time.sleep(1)