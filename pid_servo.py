from simple_pid import PID
#from motion_controller import MotionController

class PIDServo:
    #min/max ang in degrees. max_speed should be in degrees/second. initial_set in degrees
    def __init__(self, port, controller, upper_ang, min_limit, max_limit, max_speed, P, I, D, initial_set) -> None:
        self.upper_ang = upper_ang 
        self.controller = controller
        self.controller.set_servo_range(port, upper_ang)
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.max_speed = max_speed
        self.pid = PID(P, I, D, setpoint=initial_set)
        self.pid.setpoint = initial_set
        self.port = port #port on PWM board (in motion_controller)
        self.theta = initial_set #current position
        self.followers = [] #followers start empty and are added by the followers themselves when initialized
        self.controller.set_servo(port, initial_set)

    #adds a follower and sets its position to match theta of this servo
    def add_follower(self, servo):
        self.followers.append(servo)
        servo.set(self.theta)

    def set_pid(self, P, I, D):
        self.pid(P, I, D)

    def set_range(self, upper_ang):
        self.upper_ang = upper_ang

    def get_setpoint(self):
        return self.pid.setpoint

    #setpoint shall be angle
    def set_setpoint(self, setpoint):
        if(setpoint < self.min_limit):
            setpoint = self.min_limit
        elif(setpoint > self.max_limit):
            setpoint = self.max_limit
        #print("setpoint at servo", self.port, "to", setpoint)
        self.pid.setpoint = setpoint

    def update(self, delta_time):
        control = self.pid(self.theta) #result shall be angle to turn in this frame (every 20 ms)
        if(control + self.theta > self.max_limit):
            control = self.max_limit - self.theta
        elif(control + self.theta < self.min_limit):
            control = self.min_limit - self.theta
        #add upper limit to speed based on time in this frame
        elif(control / delta_time > self.max_speed):
            control = self.max_speed
        #resulting control from pid will be added to current position
        self.theta += control
        self.controller.set_servo(self.port, self.theta)
        #update any servo followers attached to this servo
        for follower in self.followers:
            follower.set(self.theta)


#Follows another servo whenever that servo is set.  Adds itself to the PID_Servo's list of followers and will update with that PID_Servo
class ServoFollower:
    #offset ang should be difference in relative angle (at zero for example)  If reveresed, difference should be positive from max_ang -> following angle
    def __init__(self, port : int, follow_servo : PIDServo, upper_ang, reversed : bool, offset_ang) -> None:
        self.port = port #port on PWM board of this servo
        self.follow_servo = follow_servo
        self.upper_ang = upper_ang
        self.reversed = reversed
        self.offset_ang = offset_ang
        self.follow_servo.add_follower(self) #port on PWM board to follow.  Add this follower to the PID_Servos followers
        pass

    def set(self, ang):
        if(self.reversed):
            ang = self.upper_ang - (ang+self.offset_ang)
        else:
            ang += self.offset_ang
        self.follow_servo.controller.set_servo(self.port, ang)
