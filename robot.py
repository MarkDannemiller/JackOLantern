# import face_recognition
import cv2
import time
import random
from motion_controller import MotionController
from face_tracker import FaceTracker
from face_tracker import screen_to_angle

video_capture = cv2.VideoCapture(0)
tracker = FaceTracker(video_capture)
controller = MotionController()

delta_time = 0.01 #time in seconds per frame
target_wait = random.randrange(3,11)
timer = 0

while True:
    initial_time = time.time()
    tracker.process()

    # update target setpoint for motion controller
    if(tracker.target_info(tracker.target)[4] > 0):
        if(timer > target_wait):
            tracker.get_new_target()
            timer = 0
            target_wait = random.randrange(3,11)

        x, y = tracker.target_info(tracker.target)[:2]
        x_deg, y_deg = screen_to_angle(x, y)
        controller.look_neck(x_deg, y_deg)
        controller.look_eyes(x_deg, y_deg)
        controller.feed_motors(delta_time)
        
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    delta_time = time.time() - initial_time #calc time frame lasted
    timer += delta_time

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()