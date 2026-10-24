import RPi.GPIO as GPIO
from simple_pid import PID
from timeit import default_timer as timer
from multiprocessing import Process, Value

'''
This class will run a stepper motor to a desired setpoint.  Through multithreading, a PID controller
generates a control velocity for the motor based on the error between the setpoint and current position.
A secondary "run" process will continuously move the stepper at the set speed.

set_active() will enable/disable module
rehome() will trigger rehoming sequence
set_setpoint() and set_setpoint_relative() will update the module's target position
feed() must be called in the update loop of the module initializing this class (feeds PID)
'''
class PIDStepper:
    
    def __init__(self, enable_pin, dir_pin, step_pin, home_switch, gear_ratio, s_p_rev, 
                    upper_ang, max_speed, error_threshold, P, I, D, neutral_pos) -> None:
        #constants
        self.GEAR_RATIO = gear_ratio
        self.S_P_REV = s_p_rev
        self.UPPER_ANG = upper_ang
        self.REHOME_DELAY = (1 / (0.025 * self.S_P_REV * self.GEAR_RATIO))
        self.MAX_SPEED = max_speed
        self.ERR_THRESH = error_threshold
        self.NEUTRAL = neutral_pos

        self.pid = PID(P, I, D, setpoint=neutral_pos) #setpoint in degrees

        self.theta = Value('d', neutral_pos) #updated position value factors into error calc
        self.velocity = Value('d', 0) #velocity in deg/second
        self.rehome_flag = Value('b', True) #raise flag to rehome
        self.enabled = True

        self.en_pin = enable_pin
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.home_switch = home_switch #limit switch return for rehome

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.home_switch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.output(enable_pin, GPIO.HIGH) #disable

        self.process = Process(target=self.__run, args=(self.velocity, self.rehome_flag))
        self.process.start()

    #process handles stepping motor and rehoming based on velocity value and rehome flag
    def __run(self, velocity, rehome_flag):
        while(1):
            if(rehome_flag.value):
                self.__home()
            else:
                #DISABLE if not moving
                if(velocity == 0):
                    GPIO.output(self.enable_pin, GPIO.HIGH)
                    continue

                if(velocity > 0):
                    self.theta.value += self.step_to_deg(1)
                    GPIO.output(self.dir_pin, GPIO.HIGH)
                else:
                    self.theta.value -= self.step_to_deg(1)
                    GPIO.output(self.dir_pin, GPIO.LOW)

                #step for delay converted from angular velocity
                delay = self.vel_to_delay(velocity)
                self.__step(delay)

    #enable/disable module
    def set_active(self, val):
        self.enabled = val
    
    #sets rehome flag high for run() process to handle
    def rehome(self):
        self.rehome_flag.value = True

    #physically moves motor until hitting home limit switch
    def __home(self):
        #do rehome logic
        while(not GPIO.input(self.home_switch)):
            self.__step(self.REHOME_DELAY)
        self.rehome_flag.value = False
        self.set_setpoint(self.NEUTRAL)

    #steps for a specified delay
    #enable and pulse the stepper driver, delay until finished
    def __step(self, delay):
        GPIO.output(self.en_pin, GPIO.LOW)
        start = timer()
        GPIO.output(self.step_pin, GPIO.HIGH)
        GPIO.output(self.step_pin, GPIO.LOW)
        while(timer()-start < delay): pass

    #sets PID setpoint to be accelerated to based on PID controller config
    def set_setpoint(self, setpoint):
        self.pid.setpoint = min(self.UPPER_ANG, max(0, setpoint)) #constrain setpoint (0, UPPER)

    #sets the setpoint as offset from current position
    def set_setpoint_relative(self, offset):
        self.set_setpoint(self.theta.value + offset)

    #should be called by upper level update loop to feed pid
    def feed(self, delta_time):
        #velocity to zero when disabled or within error threshold
        if(not self.enabled or abs(self.theta - self.pid.setpoint) < self.ERR_THRESH):
            self.velocity.value = 0
            return
        
        control = self.pid(self.theta)
        if(GPIO.input(self.home_switch) and control < 0):
            control = 0 #do not exceed limit switch
        elif(control / delta_time > self.MAX_SPEED):
            control = self.MAX_SPEED * delta_time #scaled to delta time since last frame
        self.velocity.value = control

    def step_to_deg(self, steps):
        return float(steps)/(self.S_P_REV * self.GEAR_RATIO) * 360

    #converts angular velocity in deg/second to delay period
    # 360 [deg/rev] / velocity [deg/second] = seconds/rev
    # seconds/rev * [rev/step] = seconds/step
    def vel_to_delay(self, velocity) -> float:
        return (360 / (abs(velocity)*self.S_P_REV))