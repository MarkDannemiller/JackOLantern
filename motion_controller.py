from simple_pid import PID

#SERVO BOARD CONTROL
import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
import adafruit_motor.servo
servo = adafruit_motor.servo.Servo(servo_channel)
kit = ServoKit(channels=16)
i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)

kit.servo[0].set_pulse_width_range(500, 2500)
kit.servo[1].set_pulse_width_range(500, 2500)
servokit.servo[0].actuation_range = 270
servokit.servo[1].actuation_range = 270

pca.frequency = 100

yaw_lim_right = 1000 #limit in steps to the right
yaw_lim_left = 0 #limit in steps to left
pitch_lim_lower = 0 #limit in degrees for lower neck pitch
pitch_lim_upper = 90 #limit in degrees for upper neck pitch

P_pitch = 1
I_pitch = 0
D_pitch = 0

P_yaw = 1
I_yaw = 0
D_yaw = 0

class MotionController:
    def __init__(self):
        self.pitch_pid = PID(P_pitch, I_pitch, D_pitch)
        self.yaw_pid = PID(P_pitch, I_pitch, D_pitch)
    
    def enable():
        #code to enable power to motors
        pass
    
    def disable():
        #code to disable power to motors
        pass

    def feed_motors():
        #code to feed all motors current pid values
        pass

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
#endregion

    def set_servo(port, ang, max_ang):

        pass

#region JAW
    def set_jaw(angle_left, angle_right):
        kit.servo[0].angle = angle_left
        kit.servo[1].angle = angle_right
        pass
#endregion

