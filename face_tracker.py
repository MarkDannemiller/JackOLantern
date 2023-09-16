import cv2


class Face:
    # empty constructor
    def __init__(self):
        self.h = None
        self.w = None
        self.y = None
        self.x = None

    # constructor with position info
    def __int__(self, face_id, x, y, w, h):
        self.face_id = face_id
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    # update position
    def update(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    # returns whether position of face falls within threshold when compared to another pos
    def compare_pos(self, x, y, thresh_per):
        pass


# tracks faces on a screen using computer vision
class FaceTracker:
    def __init__(self, video_capture):
        self.video_capture = video_capture
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.face_locations = []

    # update face locations
    def process(self):
        # Grab a single frame of video
        ret, frame = self.video_capture.read()
        # Convert the frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detect faces in the grayscale frame
        processed_locations = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in processed_locations:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow('Video', frame)
