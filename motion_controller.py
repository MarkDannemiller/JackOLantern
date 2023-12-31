from simple_pid import PID
import time
from multiprocessing import Process, Value
import random
import math

#SERVO BOARD CONTROL
from adafruit_servokit import ServoKit #Special library for 16 channel pwm adafruit board controlling servos
from pid_servo import PIDServo
from pid_servo import ServoFollower
from pid_stepper import PIDStepper

import RPI.GPIO as GPIO
#eye led
from gpiozero import LED

import stepper


class MotionController:
    def __init__(self):
        #region SERVO_PORTS
        self.port_eye_y = 0
        self.port_eye_x = 1
        self.port_lid_tl = 2
        self.port_lid_tr = 3
        self.port_lid_bl = 4
        self.port_lid_br = 5
        self.port_jaw_l = 6
        self.port_jaw_r = 7
        self.port_neck_l = 8
        self.port_neck_r = 9
        #endregion

        self.led_eye_l = LED(pin=23, initial_value=False)
        self.led_eye_r = LED(pin=24, initial_value=False)

        #region NECK_YAW
        self.port_yaw_en = 13
        self.port_yaw_dir = 19
        self.port_yaw_step = 26
        self.port_yaw_home = 22 #////////TBD

        GPIO.setmode(GPIO.BCM)

        #set additional ports high for 3.3v power
        self.port_yaw_vcc = 29
        self.port_lim_vcc = 31
        GPIO.setup(self.port_yaw_vcc, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.port_lim_vcc, GPIO.OUT, initial=GPIO.HIGH)

        self.yaw_lim_upper = 120 #upper limit in degrees
        self.yaw_neutral = 60
        self.yaw_gear_ratio = 3
        self.yaw_s_p_rev = 3200
        self.yaw_max_speed = 5 #deg/sec
        self.yaw_err_thresh = 5 #within 5 degrees is on target

        self.P_yaw = 0.01
        self.I_yaw = 0
        self.D_yaw = 0.05
        #endregion

        #region EYES
        self.eye_offset = 46.8 #height offset in mm of eyes
        self.size_scalar = 0.05 #relationship of face size to mm away from camera

        self.eye_lim_y_upper = 70
        self.eye_lim_y_lower = 0
        self.eye_lim_x_right = 0
        self.eye_lim_x_left = 70
        self.eye_x_neutral = 30
        self.eye_y_neutral = 35

        self.lid_ltop_close = 82
        self.lid_lbot_close = 0
        self.lid_rtop_close = 0
        self.lid_rbot_close = 80
        self.lid_ltop_open = 0
        self.lid_lbot_open = 80
        self.lid_rtop_open = 85
        self.lid_rbot_open = 0
        #endregion

        #region NECK_PITCH
        self.pitch_lim_lower = 180 #limit in degrees for lower neck pitch
        self.pitch_lim_upper = 265 #limit in degrees for upper neck pitch
        self.pitch_neutral_pos = 250 #neutral, looking forward position of neck pitch
        self.pitch_sleep_pos = 240
        self.servo_neck_offset = -15 #offset from the right neck servo
        self.neck_pitch_mv = 10 #max velocity deg/sec

        #neck servo pid
        self.P_pitch = 0.02
        self.I_pitch = 0
        self.D_pitch = 0#0.001
        #endregion

        self.lim_jaw_closed = -3
        self.lim_jaw_open = 22
        self.jaw_setpoint = self.lim_jaw_open-self.lim_jaw_closed #jaw will take input from 0-25 range
        self.jaw_mv = 100 #max velocity deg/sec


        #init
        self.kit = ServoKit(channels=16)
        self.kit.servo[self.port_jaw_l].actuation_range = 270
        self.kit.servo[self.port_jaw_r].actuation_range = 270
        self.kit.servo[self.port_neck_r].actuation_range = 270
        self.servo_neck_r = PIDServo(self.port_neck_r, self, 270, self.pitch_lim_lower, self.pitch_lim_upper, self.neck_pitch_mv, self.P_pitch, self.I_pitch, self.D_pitch, self.pitch_neutral_pos)
        self.servo_neck_l = ServoFollower(self.port_neck_l, self.servo_neck_r, 270, True, self.servo_neck_offset)

        #start stepper thread
        '''self.process = Process(target=stepper.motor, args=(stepper.setpoint, stepper.current_pos))
        self.process.start()
        self.stepper_timer = 0
        self.stepper_update_interval = 0.5
        self.stepper_ang = 0'''

        #PID stepper init
        self.yaw_stepper = PIDStepper(self.port_yaw_en, self.port_yaw_dir, self.port_yaw_step, self.port_yaw_home, self.yaw_gear_ratio, self.yaw_s_p_rev, 
                                        self.yaw_lim_upper, self.yaw_max_speed, self.yaw_err_thresh, self.P_yaw, self.I_yaw, self.D_yaw, self.yaw_neutral)

        self.sleep()
        self.led_eye_l.off()
        self.led_eye_r.off()
        time.sleep(2) #pause

        #open eyelids and set eyes to neutral
        self.set_servo(self.port_lid_bl, self.lid_lbot_open)
        self.set_servo(self.port_lid_br, self.lid_rbot_open)
        self.set_servo(self.port_lid_tl, self.lid_ltop_open)
        self.set_servo(self.port_lid_tr, self.lid_rtop_open)

        self.set_jaw(self.jaw_setpoint, 100) #set to open position

        self.blink_timer = 0
        self.blink_wait = 1
        self.blink_time = 0.25

        #led flash on sequence
        self.led_eye_l.on()
        self.led_eye_r.on()
        time.sleep(0.2)
        self.led_eye_l.off()
        self.led_eye_r.off()
        time.sleep(0.75)
        self.led_eye_l.on()
        self.led_eye_r.on()
        time.sleep(0.15)
        self.led_eye_l.off()
        self.led_eye_r.off()
        time.sleep(0.3)
        self.led_eye_l.on()
        self.led_eye_r.on()
        time.sleep(0.1)
        self.led_eye_l.off()
        self.led_eye_r.off()
        time.sleep(0.2)
        self.led_eye_l.on()
        self.led_eye_r.on()
        time.sleep(0.1)
        self.led_eye_l.off()
        self.led_eye_r.off()
        time.sleep(0.15)
        self.led_eye_l.on()
        self.led_eye_r.on()
        time.sleep(0.1)
        self.led_eye_l.off()
        self.led_eye_r.off()
        time.sleep(0.1)
        self.led_eye_l.on()
        self.led_eye_r.on()

    def enable():
        #code to enable power to motors
        pass

    #move to sleeping position
    def sleep(self):
        self.set_servo(self.port_lid_bl, self.lid_lbot_close)
        self.set_servo(self.port_lid_br, self.lid_rbot_close)
        self.set_servo(self.port_lid_tl, self.lid_ltop_close)
        self.set_servo(self.port_lid_tr, self.lid_rtop_close)
        self.look_eyes(0, 0, 0)
        self.servo_neck_r.set_setpoint(self.pitch_sleep_pos)
        self.set_jaw(0, 100) #set to closed

        self.yaw_stepper.set_setpoint(self.yaw_stepper.NEUTRAL)
        pass

    def feed_motors(self, delta_time):
        #code to feed all motors current pid values
        self.servo_neck_r.feed(delta_time)
        self.yaw_stepper.feed(delta_time)
        self.blink_timer += delta_time

        '''self.stepper_timer += delta_time
        if(self.stepper_timer > self.stepper_update_interval):
            stepper.set_setpoint(self.stepper_ang)
            self.stepper_timer = 0'''
        
        if(self.blink_timer > self.blink_wait + self.blink_time):
            self.blink_wait = 0.1*random.randrange(20,61)
            self.blink_eyes(False)
            self.blink_timer = 0
        elif(self.blink_timer > self.blink_wait):
            self.blink_eyes(True)

    def __test_servos(self):
        for i in range(0,8):
            print("servo:", i)
            ang = 270 if i >= self.port_jaw_l else 180
            self.kit.servo[i].angle = 0
            time.sleep(0.5)
            self.kit.servo[i].angle = ang
            time.sleep(0.5)

    #region NECK       
    def home_neck(self):
        #code to home neck yaw and set pitch on servos to 0
        self.servo_neck_r.set_setpoint(self.pitch_neutral_pos)
        self.yaw_stepper.rehome()
        #need limit switch for this
        pass

    #switches necks current focus
    def look_neck(self, xdegrees, ydegrees):
        self.servo_neck_r.set_setpoint(ydegrees + self.servo_neck_r.get_pos()) #offset by pitch_lim_lower such that 0 degree input corresponds with the lower
        self.yaw_stepper.set_setpoint_relative(xdegrees)
        #self.stepper_ang  = xdegrees
        #print(self.servo_neck_r.get_pos())
        #stepper.set_setpoint(xdegrees)
        #stepper.setpoint.value = int(((xdegrees*stepper.gear_ratio)/(360.0*stepper.s_p_rev)))
        #print("stepper to:", ((xdegrees*stepper.gear_ratio*stepper.s_p_rev)/360.0)) 
    #endregion

    #region EYES

    def look_eyes(self, xdegrees, ydegrees, face_size):
        xpos = -xdegrees + self.eye_x_neutral
        #y angle is a function of the vertical offset of the camera and the eyes
        '''try:
            ypos = math.atan((self.eye_offset / (face_size * self.size_scalar)) - math.tan(ydegrees)) + self.eye_y_neutral
        except:'''
        ypos = ydegrees + self.eye_y_neutral - 5

        #clamp xpos within bounds
        if(xpos < self.eye_lim_x_right):
            xpos = self.eye_lim_x_right
        elif(xpos > self.eye_lim_x_left):
            xpos = self.eye_lim_x_left

        #clamp ypos within bounds
        if(ypos < self.eye_lim_y_lower):
            ypos = self.eye_lim_y_lower
        elif(ypos > self.eye_lim_y_upper):
            ypos = self.eye_lim_y_upper

        self.set_servo(self.port_eye_x, xpos)
        self.set_servo(self.port_eye_y, ypos)

    def blink_eyes(self, pos):
        if(pos):
            self.set_servo(self.port_lid_tl, self.lid_ltop_close)
            self.set_servo(self.port_lid_bl, self.lid_lbot_close)
            self.set_servo(self.port_lid_tr, self.lid_rtop_close)
            self.set_servo(self.port_lid_br, self.lid_rbot_close)
        else:
            self.set_servo(self.port_lid_tl, self.lid_ltop_open)
            self.set_servo(self.port_lid_bl, self.lid_lbot_open)
            self.set_servo(self.port_lid_tr, self.lid_rtop_open)
            self.set_servo(self.port_lid_br, self.lid_rbot_open)
    #endregion

    def set_servo(self, port, ang):
        self.kit.servo[port].angle = ang
        #print("move servo", port, "to:", ang)

    def set_servo_range(self, port, upper_ang):
        self.kit.servo[port].actuation_range = upper_ang

    #region JAW, pass large delta_time to set to angle as fast as possible
    def set_jaw(self, angle, delta_time):
        #floor at 0 (will be translated to lower limit)
        if(angle < 0):
            angle = 0
        elif(angle > self.lim_jaw_open-self.lim_jaw_closed):
            angle = self.lim_jaw_open-self.lim_jaw_closed
        
        angle += self.lim_jaw_closed

        #calculate an updated position based on time elapsed and maximum velocity
        updated_pos = self.jaw_setpoint + (angle-self.jaw_setpoint) * self.jaw_mv * delta_time
        
        #prevent overshoot
        if((self.jaw_setpoint < angle and updated_pos <= angle) or self.jaw_setpoint > angle and updated_pos >= angle):
            self.jaw_setpoint = updated_pos
        else:
            self.jaw_setpoint = angle

        #pass angle and this code should sync motors
        self.set_servo(self.port_jaw_l, 100 + self.jaw_setpoint)
        self.set_servo(self.port_jaw_r, 100 - self.jaw_setpoint)
    #endregion



#region TEST_CODE

#neck servo test
'''
kit.servo[port_neck_l].angle = 64 #goes down for more range
kit.servo[port_neck_r].angle = 202 #goes up for more range
time.sleep(1)
kit.servo[port_neck_l].angle = 170
kit.servo[port_neck_r].angle = 100
'''

#test limits and neutral position
'''
controller = MotionController()
controller.set_jaw(-3, 100)
time.sleep(1)
controller.set_jaw(22, 100)
time.sleep(1)
controller.set_jaw(-3, 100)'''

'''stepper.set_setpoint(30)
time.sleep(3)
stepper.set_setpoint(-30)'''

#controller = MotionController()
#minimum
#controller.set_servo(controller.port_neck_l, 100)
#controller.set_servo(controller.port_neck_r, 173)
'''time.sleep(5)
#neutral position
controller.set_servo(controller.port_neck_l, 51)
controller.set_servo(controller.port_neck_r, 194)
time.sleep(5)
#maximum
controller.set_servo(controller.port_neck_l, 41)
controller.set_servo(controller.port_neck_r, 204)'''

'''
//this is a comment
'''

'''
#eye test motion
setpoint = 0

set_servo(port_eye_y, setpoint)
set_servo(port_eye_x, setpoint)
'''

'''
for x in range(0, 10):

    eye_lid_left_top_close = 80
    eye_lid_left_bot_close = 0


    set_servo(port_lid_tl, eye_lid_left_top_close)
    set_servo(port_lid_bl, eye_lid_left_bot_close)

    eye_lid_right_top_close = 0
    eye_lid_right_bot_close = 80
    set_servo(port_lid_tr, eye_lid_right_top_close)
    set_servo(port_lid_br, eye_lid_right_bot_close)
    time.sleep(0.5)

    eye_lid_left_top_open = 0
    eye_lid_left_bot_open = 85
    set_servo(port_lid_tl, eye_lid_left_top_open)
    set_servo(port_lid_bl, eye_lid_left_bot_open)

    eye_lid_right_top_open = 85
    eye_lid_right_bot_open = 0
    set_servo(port_lid_tr, eye_lid_right_top_open)
    set_servo(port_lid_br, eye_lid_right_bot_open)

    time.sleep(0.5)
'''
#endregion