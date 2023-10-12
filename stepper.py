import RPi.GPIO as GPIO
from time import sleep
from timeit import default_timer as timer
from multiprocessing import Process, Value
from random import randrange

gear_ratio = 3
high_speed = 0.1
low_speed = 0.025
s_p_rev = 3200
min_steps = 160
low_speed_delay = (1 / (low_speed * s_p_rev * gear_ratio))
high_speed_delay = (1 / (high_speed * s_p_rev * gear_ratio))
accel_factor = 1/(((3/low_speed_delay-high_speed_delay))/8)*min_steps

neutral_pos = 0

setpoint = Value('i', 0)
current_pos = Value('d', 0.0)

enable_pin = 13
dir_pin = 19
step_pin = 26

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(enable_pin, GPIO.OUT)
GPIO.setup(dir_pin, GPIO.OUT)
GPIO.setup(step_pin, GPIO.OUT)

GPIO.output(enable_pin, GPIO.HIGH)

def get_pos():
    global current_pos
    return current_pos.value

#steps to degrees conversion
def step_to_deg(steps):
    return float(steps)/(s_p_rev*gear_ratio) * 360

def home():
    #first do code to reset at limit switch (UNIMPLEMENTED)
    '''while(not limit_switch):
        set_setpoint(-500)
        sleep(0.5)
    set_setpoint(0)
    sleep(1)
        '''
    #next return to neutral position
    set_setpoint(get_forward_ang())

def get_forward_ang():
    return neutral_pos - get_pos()

def set_setpoint(theta):
    global setpoint
    setpoint.value = int(((theta*gear_ratio*s_p_rev)/(360)))
    #print("converted", theta, "to steps:", setpoint.value)

def motor(setpoint, current_pos):
    prev_setpoint = 0
    curr_setpoint = 0
    steps = 0
    while(1):
        curr_setpoint = setpoint.value
        start = timer()
        if(abs(prev_setpoint - curr_setpoint) > 10):
            steps = setpoint.value
        if(setpoint.value != 0 and steps != 0):
            if(steps < 0):
                GPIO.output(dir_pin, GPIO.LOW)
                steps += 1
                current_pos.value -= 1
                GPIO.output(enable_pin, GPIO.LOW)
            elif(steps > 0):
                GPIO.output(dir_pin, GPIO.HIGH)
                steps -= 1
                current_pos.value += 1
                GPIO.output(enable_pin, GPIO.LOW)
            GPIO.output(step_pin, GPIO.HIGH)
            GPIO.output(step_pin, GPIO.LOW)
            delay = ((1.5*accel_factor*abs(setpoint.value))/steps)*(abs(setpoint.value)-steps) + low_speed_delay
            if(delay < high_speed_delay):
                delay = high_speed_delay
            prev_setpoint = curr_setpoint
            while(timer()-start < delay): pass
        else:
            GPIO.output(enable_pin, GPIO.HIGH)
   
if(__name__ == '__main__'):
    process = Process(target=motor, args=(setpoint, current_pos,))
    process.start()
    sleep(0.1)
    angles = [30, 15, 5, 0, 0, -10, -15, -5, 5, 15, -10, -10, -10, -10, 0, 0, 0, 0]
    for angle in angles:
        set_setpoint(angle)
        sleep(0.5)
    process.terminate()