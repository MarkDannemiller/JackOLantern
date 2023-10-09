# import face_recognition
import cv2
import time
from timeit import default_timer as timer
import random
from multiprocessing import Process, Value

from motion_controller import MotionController
from face_tracker import FaceTracker
from face_tracker import screen_to_angle

video_capture = cv2.VideoCapture(0)
tracker = FaceTracker(video_capture)
controller = MotionController()

delta_time = 0.02 #time in seconds per frame
target_wait = random.randrange(3,11)
timer = 0

x_deg = Value('d', 0)
y_deg = Value('d', 0)

def update_motion(x_deg, y_deg):
    while(True):
        initial_time = timer()

        controller.look_neck(x_deg.value, y_deg.value)
        controller.look_eyes(x_deg.value, y_deg.value)
        controller.feed_motors(delta_time)

        while(timer() - initial_time < delta_time):
            pass

motor_process = Process(target=update_motion, args=(x_deg, y_deg))
motor_process.start()
time.sleep(0.1)

while True:
    initial_time = timer()
    tracker.process()

    # update target setpoint for motion controller
    if(tracker.target_info(tracker.target)[4] > 0):

        #update target based on timer AND duration of frame
        if(timer > target_wait):
            tracker.get_new_target()
            timer = 0
            target_wait = random.randrange(3,11)

        x, y = tracker.target_info(tracker.target)[:2]
        x_deg.value, y_deg.value = screen_to_angle(x, y)
        
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        controller.process.terminate()
        break

    diff_time = timer() - initial_time #calc time frame lasted
    timer += delta_time

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()