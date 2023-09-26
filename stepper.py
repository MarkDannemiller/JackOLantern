import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
 
class Stepper:
    def __init__(self, step_pin, dir_pin):
        self.step_pin = step_pin
        GPIO.setup(step_pin, GPIO.OUT)
        self.dir_pin = dir_pin
        GPIO.setup(dir_pin, GPIO.OUT)
        self.position = 0
 
    def set_speed(self, speed):
        self.delay = 1 / abs(speed)  # delay in seconds
 
    def set_direction(self, direction):
        GPIO.output(self.dir_pin, direction)
 
    def move_to(self, position):
        self.set_direction(position > self.position)
        while self.position != position:
            GPIO.output(self.step_pin, True)
            time.sleep(self.delay)
            GPIO.output(self.step_pin, False)
            self.position += 1 if position > self.position else -1
 
# Define the pins
step_pin = 27  # GPIO number where step pin is connected
dir_pin = 22   # GPIO number where dir pin is connected
 
# Initialize stepper
stepper = Stepper(step_pin, dir_pin)
 
def loop():
    while True:
        # Move forward 2 revolutions (400 steps) at 200 steps/sec
        print("speed:", 200, "move:", 400)
        stepper.set_speed(200)
        stepper.move_to(400)
        time.sleep(1)
 
        # Move backward 1 revolution (200 steps) at 600 steps/sec
        print("speed:", 100, "move:", 200)
        stepper.set_speed(400)
        stepper.move_to(200)
        time.sleep(1)
 
        # Move forward 3 revolutions (600 steps) at 400 steps/sec
        print("speed:", 100, "move:", 600)
        stepper.set_speed(300)
        stepper.move_to(600)
        time.sleep(1)

loop()