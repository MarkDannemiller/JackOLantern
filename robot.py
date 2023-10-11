# import face_recognition
import cv2
import time
from timeit import default_timer as timer
import random
from multiprocessing import Process, Value

from motion_controller import MotionController
import stepper
from face_tracker import FaceTracker
from face_tracker import screen_to_angle

video_capture = cv2.VideoCapture(0)
tracker = FaceTracker(video_capture)
controller = MotionController()

delta_time = 0.02 #time in seconds per frame
target_wait = random.randrange(3,11)
target_timer = 0
no_face_wait = 3.0 #wait this many seconds before moving back to neutral position
no_face_timer = 0

x_deg_neck = Value('d', 0)
y_deg_neck = Value('d', 0)
x_deg_eyes = Value('d', 0)
y_deg_eyes = Value('d', 0)

def update_motion(x_deg_neck, y_deg_neck, x_deg_eyes, y_deg_eyes):
    while(True):
        initial_time = timer()

        controller.look_neck(x_deg_neck.value, y_deg_neck.value)
        controller.look_eyes(x_deg_eyes.value, y_deg_eyes.value)
        controller.feed_motors(delta_time)

        while(timer() - initial_time < delta_time):
            pass

motor_process = Process(target=update_motion, args=(x_deg_neck, y_deg_neck, x_deg_eyes, y_deg_eyes))
motor_process.start()
time.sleep(0.1)

while True:
    initial_time = timer()
    frame = tracker.process()
    cv2.imshow('face', frame) #comment out for performance

    face_cnt = tracker.target_info(tracker.target)[4]

    # update target setpoint for motion controller
    if(face_cnt > 0):
        no_face_timer = 0
        #update target based on timer AND duration of frame
        if(target_timer > target_wait):
            tracker.get_new_target()
            target_timer = 0
            target_wait = random.randrange(3,11)

        x, y = tracker.target_info(tracker.target)[:2]
        x_deg_neck.value, y_deg_neck.value = screen_to_angle(x, y)
        x_deg_eyes.value, y_deg_eyes.value = x_deg_neck.value, y_deg_neck.value
    else:
        no_face_timer += delta_time
        #look back to forward position after not seeing face for long enough
        if(no_face_timer > no_face_wait):
            y_deg_neck.value = 0 #neutral y
            y_deg_eyes.value = controller.pitch_neutral_pos - controller.servo_neck_r.get_setpoint()
            x_deg_neck.value = stepper.get_forward_ang()
            x_deg_eyes.value = x_deg_neck.value #eyes will look at same point in horizontal
        
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        controller.process.terminate()
        break

    diff_time = timer() - initial_time #calc time frame lasted
    target_timer += diff_time

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()