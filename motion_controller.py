from simple_pid import PID
import time
from multiprocessing import Process, Value
import random

#SERVO BOARD CONTROL
from adafruit_servokit import ServoKit #Special library for 16 channel pwm adafruit board controlling servos
from pid_servo import PIDServo
from pid_servo import ServoFollower

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

        self.eye_lim_y_upper = 70
        self.eye_lim_y_lower = 0
        self.eye_lim_x_right = 0
        self.eye_lim_x_left = 70
        self.eye_x_neutral = 30
        self.eye_y_neutral = 35

        self.lid_ltop_close = 80
        self.lid_lbot_close = 0
        self.lid_rtop_close = 0
        self.lid_rbot_close = 80
        self.lid_ltop_open = 0
        self.lid_lbot_open = 85
        self.lid_rtop_open = 85
        self.lid_rbot_open = 0

        self.yaw_lim_right = 1000 #limit in steps to the right
        self.yaw_lim_left = 0 #limit in steps to left
        self.pitch_lim_lower = 130 #limit in degrees for lower neck pitch
        self.pitch_lim_upper = 204 #limit in degrees for upper neck pitch
        self.pitch_neutral_pos = 194 #neutral, looking forward position of neck pitch
        self.servo_neck_offset = 20 #offset from the right neck servo
        self.neck_pitch_mv = 10 #max velocity deg/sec

        #neck servo pid
        self.P_pitch = 0.03
        self.I_pitch = 0
        self.D_pitch = 0#0.001

        self.lim_jaw_upper = -3
        self.lim_jaw_lower = 22

        '''self.P_yaw = 0.01
        self.I_yaw = 0
        self.D_yaw = 0.05'''

        #init
        self.kit = ServoKit(channels=16)
        self.kit.servo[self.port_jaw_l].actuation_range = 270
        self.kit.servo[self.port_jaw_r].actuation_range = 270
        self.kit.servo[self.port_neck_r].actuation_range = 270
        self.servo_neck_r = PIDServo(self.port_neck_r, self, 270, self.pitch_lim_lower, self.pitch_lim_upper, self.neck_pitch_mv, self.P_pitch, self.I_pitch, self.D_pitch, self.pitch_neutral_pos)
        self.servo_neck_l = ServoFollower(self.port_neck_l, self.servo_neck_r, 270, True, self.servo_neck_offset)

        #start stepper thread
        self.process = Process(target=stepper.motor, args=(stepper.setpoint, ))
        self.process.start()
        self.stepper_timer = 0
        self.stepper_update_interval = 0.5
        self.stepper_ang = 0

        #open eyelids and set eyes to neutral
        self.set_servo(self.port_lid_bl, self.lid_lbot_open)
        self.set_servo(self.port_lid_br, self.lid_rbot_open)
        self.set_servo(self.port_lid_tl, self.lid_ltop_open)
        self.set_servo(self.port_lid_tr, self.lid_rtop_open)
        self.set_servo(self.port_eye_x, self.eye_x_neutral)
        self.set_servo(self.port_eye_y, self.eye_y_neutral)

        self.set_jaw(-3) #set to 0 position

        self.blink_timer = 0
        self.blink_wait = 1
        self.blink_time = 0.25

    def enable():
        #code to enable power to motors
        pass

    def disable():
        #code to disable power to motors
        pass

    def feed_motors(self, delta_time):
        #code to feed all motors current pid values
        self.servo_neck_r.update(delta_time)
        self.stepper_timer += delta_time
        self.blink_timer += delta_time
        if(self.stepper_timer > self.stepper_update_interval):
            stepper.set_setpoint(self.stepper_ang)
            self.stepper_timer = 0
        
        if(self.blink_timer > self.blink_wait + self.blink_time):
            self.blink_wait = 0.1*random.randrange(20,61)
            self.blink_eyes(False)
            self.blink_timer = 0
        elif(self.blink_timer > self.blink_wait):
            self.blink_eyes(True)

    def test_servos(self):
        for i in range(0,8):
            print("servo:", i)
            ang = 270 if i >= self.port_jaw_l else 180
            self.kit.servo[i].angle = 0
            time.sleep(0.5)
            self.kit.servo[i].angle = ang
            time.sleep(0.5)

    #region NECK       
    def home_neck():
        #code to home neck yaw and set pitch on servos to 0
        #need limit switch for this
        pass

    #switches necks current focus
    def look_neck(self, xdegrees, ydegrees):
        self.servo_neck_r.set_setpoint(ydegrees + self.servo_neck_r.theta) #offset by pitch_lim_lower such that 0 degree input corresponds with the lower
        self.stepper_ang  = xdegrees
        #stepper.set_setpoint(xdegrees)
        #stepper.setpoint.value = int(((xdegrees*stepper.gear_ratio)/(360.0*stepper.s_p_rev)))
        #print("stepper to:", ((xdegrees*stepper.gear_ratio)/(360.0*stepper.s_p_rev))) 
    #endregion

    #region EYES
    def look_eyes(self, xdegrees, ydegrees):
        xpos = -xdegrees + self.eye_x_neutral
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

    #region JAW
    def set_jaw(self, angle):
        if(angle < self.lim_jaw_lower):
            angle = self.lim_jaw_lower
        elif(angle > self.lim_jaw_upper):
            angle = self.lim_jaw_upper
        #pass angle and this code should sync motors
        self.set_servo(self.port_jaw_l, 100 + angle)
        self.set_servo(self.port_jaw_r, 100 - angle)
    #endregion



#region TEST_CODE

#test_servos()

#neck servo test
'''
kit.servo[port_neck_l].angle = 64 #goes down for more range
kit.servo[port_neck_r].angle = 202 #goes up for more range
time.sleep(1)
kit.servo[port_neck_l].angle = 170
kit.servo[port_neck_r].angle = 100
'''

#test limits and neutral position

'''controller = MotionController()
controller.set_jaw(-3)
time.sleep(1)
controller.set_jaw(22)
time.sleep(1)'''
#controller.set_jaw(-3)

'''stepper.set_setpoint(30)
time.sleep(3)
stepper.set_setpoint(-30)'''
'''
#minimum
controller.set_servo(controller.port_neck_l, 120)
controller.set_servo(controller.port_neck_r, 130)
time.sleep(5)
#neutral position
controller.set_servo(controller.port_neck_l, 51)
controller.set_servo(controller.port_neck_r, 194)
time.sleep(5)
#maximum
controller.set_servo(controller.port_neck_l, 41)
controller.set_servo(controller.port_neck_r, 204)
'''
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


