# import face_recognition
import cv2
import time
from face_tracker import FaceTracker

video_capture = cv2.VideoCapture(0)
tracker = FaceTracker(video_capture)

frame_time = 0.02 #time in seconds per frame (50 fps)

while True:
    initial_time = time.time
    tracker.process()
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    #ensures that frame takes at least 20 ms
    while(time.time < initial_time + 0.02):
        print("wait", time.time)
        pass

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
