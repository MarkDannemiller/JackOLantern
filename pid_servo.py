from simple_pid import PID
from motion_controller import set_servo

class PIDServo:
    #min/max ang in degrees. max_speed should be in degrees/second. initial_set in degrees
    def __init__(self, port, upper_ang, min_ang, max_ang, max_speed, P, I, D, initial_set) -> None:
        self.upper_ang = upper_ang
        self.min_ang = min_ang
        self.max_ang = max_ang
        self.max_speed = max_speed
        self.pid = PID(P, I, D, setpoint=initial_set)
        self.setpoint = 0
        self.port = port
        self.theta = initial_set
        set_servo(port, initial_set)

    def set_pid(self, P, I, D):
        self.pid(P, I, D)

    def set_range(self, upper_ang):
        self.upper_ang = upper_ang

    def set_setpoint(self, setpoint):
        self.setpoint = setpoint
        if(self.setpoint < self.min_ang):
            self.setpoint = self.min_ang
        elif(self.setpoint > self.max_ang):
            self.setpoint = self.max_ang

    def update(self):
        control = self.pid(self.theta) #result shall be angle to turn in this frame
        if(control + self.theta > self.max_ang):
            control = self.max_ang - self.theta
        elif(control + self.theta < self.min_ang):
            control = self.min_ang - self.theta
        #resulting control from pid will be added to current position
        self.theta += self.control
        set_servo(self.port, self.theta)