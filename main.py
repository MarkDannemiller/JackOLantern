# import face_recognition
import cv2
from face_tracker import FaceTracker

video_capture = cv2.VideoCapture(0)
tracker = FaceTracker(video_capture)

while True:
    tracker.process()
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
