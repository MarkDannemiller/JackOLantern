from simple_pid import PID
import time

#SERVO BOARD CONTROL
from adafruit_servokit import ServoKit #Special library for 16 channel pwm adafruit board controlling servos

#region SERVO_PORTS
port_eye_y = 0
port_eye_x = 1
port_lid_tl = 2
port_lid_tr = 3
port_lid_bl = 4
port_lid_br = 5
port_jaw_l = 6
port_jaw_r = 7
port_neck_l = 8
port_neck_r = 9
#endregion

yaw_lim_right = 1000 #limit in steps to the right
yaw_lim_left = 0 #limit in steps to left
pitch_lim_lower = 0 #limit in degrees for lower neck pitch
pitch_lim_upper = 90 #limit in degrees for upper neck pitch

eye_lim_y_upper = 50
eye_lim_y_lower = 0
eye_lim_x_right = 90
eye_lim_x_left = 0
eyelid_lim_open = 90
eyelid_lim_close = 0

P_pitch = 1
I_pitch = 0
D_pitch = 0

P_yaw = 1
I_yaw = 0
D_yaw = 0

#init
pitch_pid = PID(P_pitch, I_pitch, D_pitch)
yaw_pid = PID(P_pitch, I_pitch, D_pitch)
kit = ServoKit(channels=16)
kit.servo[port_jaw_l].actuation_range = 270
kit.servo[port_jaw_r].actuation_range = 270
kit.servo[port_neck_l].actuation_range = 270
kit.servo[port_neck_r].actuation_range = 270

def enable():
    #code to enable power to motors
    pass

def disable():
    #code to disable power to motors
    pass

def feed_motors():
    #code to feed all motors current pid values
    pass

def test_servos():
    for i in range(0,8):
        print("servo:", i)
        ang = 270 if i >= port_jaw_l else 180
        kit.servo[i].angle = 0
        time.sleep(0.5)
        kit.servo[i].angle = ang
        time.sleep(0.5)

#region NECK       
def home_neck():
    #code to home neck yaw and set pitch on servos to 0
    pass

def set_neck(xdegrees, ydegrees):
    yaw_pid.setpoint = xdegrees
    pass
#endregion

#region EYES
def look_eyes(xdegrees, ydegrees):

    pass

def blink_eyes(pos):

    pass
#endregion

def set_servo(port, ang):
    kit.servo[port].angle = ang
    pass

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
kit.servo[port_neck_r].angle = 100m,l 
'''

#set neck servos to neutral head position
'''kit.servo[port_neck_l].angle = 75 #goes down for more range
kit.servo[port_neck_r].angle = 195 #goes up for more range
'''

#eye test motion
setpoint = 0


set_servo(port_eye_y, setpoint)
set_servo(port_eye_x, setpoint)

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

#endregion

