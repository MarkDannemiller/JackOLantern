from simple_pid import PID

class MotionController:
    def __init__(self, P, I, D):
        self.pid = PID(P, I, D)
