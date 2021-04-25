import RPi.GPIO as GPIO
import time

#GPIO SETUP
channel = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)

while True:
    print(GPIO.input(channel))
    time.sleep(0.5)
