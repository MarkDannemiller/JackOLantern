# import face_recognition
import cv2
import time
import motion_controller
from face_tracker import FaceTracker
from face_tracker import screen_to_angle

video_capture = cv2.VideoCapture(0)
tracker = FaceTracker(video_capture)

frame_time = 0.02 #time in seconds per frame

def delta_time():
    return frame_time

while True:
    initial_time = time.time
    tracker.process()

    # update target setpoint for motion controller
    if(tracker.check_info()):
        target_pos_deg = screen_to_angle(tracker.target_info[:2])
        motion_controller.look_neck(target_pos_deg)
        
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_time = time.time - initial_time #calc time frame lasted

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()