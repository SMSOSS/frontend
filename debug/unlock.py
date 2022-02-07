#Import all neccessary features to code.
import RPi.GPIO as GPIO

GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)

while (True):    
    GPIO.output(2, 0)
    print("DEBUG: lock should be unlocked")