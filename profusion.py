#!/usr/bin/env python

import RPi.GPIO as GPIO
from gpiozero import PWMOutputDevice
import time
import sys

# Input some basic timing parameters
waste_time = 5 # The amount of time in seconds you want to pump the waste
media_time = 10 # The amount of time in seconds you want to pump in fresh media
profusion_time = 2 # Amount of time in seconds you want to run profusion
cycles = 50	# How many times you want to do this

# Pin Definitions:
media_speed = PWMOutputDevice(pin = 12, frequency = 3000) # This pin controls the speed of the pump 5V is fast, 0V is slow
media_directionPin = 24 # This pin control the direction of the pump 5V CCW, 0V CW
media_enablePin = 25 # This pin turns on/off the waste/media pump
prof_speed = PWMOutputDevice(13)
prof_directionPin = 20
prof_enablePin = 21

# Pin Setup:
GPIO.setmode(GPIO.BCM)
GPIO.setup(media_directionPin, GPIO.OUT)
GPIO.setup(media_enablePin, GPIO.OUT)
GPIO.setup(prof_directionPin, GPIO.OUT)
GPIO.setup(prof_enablePin, GPIO.OUT)

# Initialize state for Pumps:
GPIO.output(media_directionPin, GPIO.LOW)
GPIO.output(prof_directionPin, GPIO.LOW)
GPIO.output(media_enablePin, GPIO.HIGH)
GPIO.output(prof_enablePin, GPIO.LOW)

print("Here we go! Press CTRL+C to exit")

while True:
  try:
    for i in range(cycles):
      print("Cycle number ",i+1)
      GPIO.output(media_directionPin, GPIO.LOW)	# Set direction to waste
      media_speed.value = .5
      time.sleep(1)
      GPIO.output(media_enablePin, GPIO.LOW)	# Turn on waste/media pump
      time.sleep(waste_time)
      GPIO.output(media_enablePin, GPIO.HIGH)	# Turn off pump
      time.sleep(0.5)
      GPIO.output(media_directionPin, GPIO.HIGH)  # Change direction of pump
      media_speed.value = .1
      time.sleep(1)
      GPIO.output(media_enablePin, GPIO.LOW)	# Turn pump back on
      time.sleep(media_time)
      GPIO.output(media_enablePin, GPIO.HIGH)	# Turn pump off again
      GPIO.output(media_directionPin, GPIO.LOW)
      GPIO.output(prof_directionPin, GPIO.LOW)
      prof_speed.value = 1
      GPIO.output(prof_enablePin, GPIO.LOW)	# Turn on profusion pump
      time.sleep(profusion_time)
    break
  except KeyboardInterrupt:
    print("shutting down nicely...")
    GPIO.output(media_enablePin, GPIO.HIGH)
    GPIO.output(prof_enablePin, GPIO.HIGH)
    GPIO.output(media_directionPin, GPIO.LOW)
    GPIO.output(prof_directionPin, GPIO.LOW)
    print("toodaloo")
    time.sleep(5)
    sys.exit()

  finally:
    print("clean up")
    GPIO.cleanup() # cleanup all GPIO
