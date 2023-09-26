import RPi.GPIO as GPIO
from time import sleep

 

high_speed = 0.5
low_speed = 0.1
interm_speed = 0.5
accel_steps = 100
deccel_steps = 100
s_p_rev = 3200
min_steps = accel_steps + deccel_steps

 

pins = [14, 15, 12, 13] #dir, step

 

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for b in pins: 
    GPIO.setup(b, GPIO.OUT)

 

def accel(steps):
    timings = []
    if(steps >= min_steps):
        speed_dif = high_speed - low_speed
        accel_jump = speed_dif / accel_steps
        deccel_jump = speed_dif / deccel_steps
        speed = low_speed
        for a in range(accel_steps):
            delay = round(((1 / speed) / s_p_rev),8)
            timings.append(delay)
            speed = round((speed + accel_jump), 8)
        delay = round(((1 / speed) / s_p_rev),8)
        for a in range((steps - (accel_steps + deccel_steps)) - 1):
            timings.append(delay)
        for a in range(deccel_steps + 1):
            delay = round(((1 / speed) / s_p_rev),8)
            timings.append(delay)
            speed = round((speed - deccel_jump), 8)
    else:
        delay = round(((1 / interm_speed) / s_p_rev),8)
        for a in range(steps):
            timings.append(delay)
    return timings

 

def motor1(dir, steps):
    timings = accel(steps)
    if(dir):
        GPIO.output(pins[0], GPIO.LOW)
    else:
        GPIO.output(pins[0], GPIO.HIGH)
    for a in range(steps):
        GPIO.output(pins[1], GPIO.HIGH)
        GPIO.output(pins[1], GPIO.LOW)
        sleep(timings[a])
        
def motor2(dir, steps):
    timings = accel(steps)
    if(dir):
        GPIO.output(pins[2], GPIO.LOW)
    else:
        GPIO.output(pins[2], GPIO.HIGH)
    for a in range(steps):
        GPIO.output(pins[3], GPIO.HIGH)
        GPIO.output(pins[3], GPIO.LOW)
        sleep(timings[a])


motor1(True, 5000)