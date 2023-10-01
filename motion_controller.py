from simple_pid import PID
import time

#SERVO BOARD CONTROL
from adafruit_servokit import ServoKit #Special library for 16 channel pwm adafruit board controlling servos
from pid_servo import PIDServo
from pid_servo import ServoFollower


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

        self.eye_lim_y_upper = 50
        self.eye_lim_y_lower = 0
        self.eye_lim_x_right = 90
        self.eye_lim_x_left = 0
        self.eyelid_lim_open = 90
        self.eyelid_lim_close = 0


        self.yaw_lim_right = 1000 #limit in steps to the right
        self.yaw_lim_left = 0 #limit in steps to left
        self.pitch_lim_lower = 64 #limit in degrees for lower neck pitch
        self.pitch_lim_upper = 100 #limit in degrees for upper neck pitch
        self.servo_neck_r_offset = 4 #offset from the right neck servo
        self.neck_pitch_mv = 10 #max velocity

        self.P_pitch = 1
        self.I_pitch = 0
        self.D_pitch = 0

        self.P_yaw = 1
        self.I_yaw = 0
        self.D_yaw = 0

        #init
        self.kit = ServoKit(channels=16)
        self.kit.servo[self.port_jaw_l].actuation_range = 270
        self.kit.servo[self.port_jaw_r].actuation_range = 270
        self.kit.servo[self.port_neck_r].actuation_range = 270
        self.servo_neck_l = PIDServo(self.port_neck_l, self, 270, self.pitch_lim_lower, self.pitch_lim_upper, self.neck_pitch_mv, self.P_pitch, self.I_pitch, self.D_pitch, self.pitch_lim_lower)
        self.servo_neck_r = ServoFollower(self.port_neck_r, self.servo_neck_l, 270, True, 4)

    def enable():
        #code to enable power to motors
        pass

    def disable():
        #code to disable power to motors
        pass

    def feed_motors(self, delta_time):
        #code to feed all motors current pid values
        self.servo_neck_l.update(delta_time)
        pass

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
        self.servo_neck_l.set_setpoint(ydegrees + self.pitch_lim_lower) #offset by pitch_lim_lower such that 0 degree input corresponds with the lower
    #endregion

    #region EYES
    def look_eyes(xdegrees, ydegrees):

        pass

    def blink_eyes(pos):

        pass
    #endregion

    def set_servo(self, port, ang):
        self.kit.servo[port].angle = ang
        print("move servo", port, "to:", ang)
        pass

    def set_servo_range(self, port, upper_ang):
        self.kit.servo[port].actuation_range = upper_ang

    #region JAW
    def set_jaw(angle):
        #pass angle and this code should sync motors
        pass
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

#set neck servos to neutral head position
'''kit.servo[port_neck_l].angle = 75 #goes down for more range
kit.servo[port_neck_r].angle = 195 #goes up for more range
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


