# import cv2

# #Jacob
# class Face:
#     # empty constructor
#     def __init__(self):
#         self.h = None
#         self.w = None
#         self.y = None
#         self.x = None

#     # constructor with position info
#     def __int__(self, face_id, x, y, w, h):
#         self.face_id = face_id
#         self.x = x
#         self.y = y
#         self.w = w
#         self.h = h

#     # update position
#     def update(self, x, y, w, h):
#         self.x = x
#         self.y = y
#         self.w = w
#         self.h = h

#     # returns whether position of face falls within threshold when compared to another pos
#     def compare_pos(self, x, y, thresh_per):
#         pass


# # tracks faces on a screen using computer vision
# class FaceTracker:
#     def __init__(self, video_capture):
#         self.video_capture = video_capture
#         self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#         self.face_locations = []

#     # update face locations
#     def process(self):
#         # Grab a single frame of video
#         ret, frame = self.video_capture.read()
#         # Convert the frame to grayscale for face detection
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         # Detect faces in the grayscale frame
#         processed_locations = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
#         for (x, y, w, h) in processed_locations:
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         cv2.imshow('Video', frame)












import cv2
import mediapipe
import random
import time

class FaceTracker:
    def __init__(self, video_capture):
        self.video_capture=video_capture
        self.mediapipe_face_detection=mediapipe.solutions.face_detection
        self.mediapipe_drawing=mediapipe.solutions.drawing_utils
        self.face_entered_square=0
        self.currently_noted={}
        self.counter_id=0
        self.id_options=list(range(10))
        self.unfilled={}
        self.text_offset=0
        self.box_state={}
        self.target=0
        self.start=0
        self.end=0
        self.x_target=0
        self.y_target=0
        self.check=1
        self.timer=0
        self.previous1=None
        self.previous2=None
        self.currently_seen=None
        self.test=0
        self.x_target_final=0
        self.y_target_final=0
        self.target_final=0
        self.start1=0
        self.in_box=0

    def process(self):
        ret, frame=self.video_capture.read()
        frame=cv2.resize(frame, (640, 480))
        if not ret:
            return

        if self.face_entered_square:
            cv2.rectangle(frame, (250, 150), (400, 300), (255, 0, 0), 1)
        self.face_entered_square=0

        with self.mediapipe_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as detector_settings:
            frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            location=detector_settings.process(frame)
            frame=cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if location.detections:
                for detection in location.detections:
                    face_pair=""
                    initial_bounding = detection.location_data.relative_bounding_box
                    boundary_box_detection=(int(initial_bounding.xmin * 640),int(initial_bounding.ymin * 480),int(initial_bounding.width * 640),int(initial_bounding.height * 480),)
                    x = int(640-initial_bounding.xmin*640)
                    y = int(480 - initial_bounding.ymin*480)
                    if (250<x<400) and (150<y<350):
                        self.face_entered_square=1

                    for id_tracker, (x_comparison, y_comparison) in self.currently_noted.items():
                        x=boundary_box_detection[0]
                        y=boundary_box_detection[1]
                        if (abs(x-x_comparison)<100) and (abs(y-y_comparison)<100):
                            face_pair=id_tracker
                            self.unfilled[id_tracker]=0
                            break
                    if face_pair!="":
                        self.unfilled[face_pair]=0
                        x_comparison, y_comparison=self.currently_noted[face_pair]
                        jitter_coordinate_x=0.9*abs(boundary_box_detection[0]-x_comparison)+x_comparison
                        jitter_coordinate_y=0.9*abs(boundary_box_detection[1]-y_comparison)+y_comparison
                        self.currently_noted[face_pair]=(jitter_coordinate_x, jitter_coordinate_y)
                        if face_pair not in self.box_state:
                            self.box_state[face_pair]=0
                        if (250<boundary_box_detection[0]<400) and (150<boundary_box_detection[1]<350):
                            self.box_state[face_pair]=1
                        else:
                            self.box_state[face_pair]=0
                    else:
                        if self.id_options:
                            face_pair=self.id_options[0]
                            del self.id_options[0]
                    self.currently_noted[face_pair]=(boundary_box_detection[0], boundary_box_detection[1])
                    self.unfilled[face_pair]=0
                    self.text_offset=20
                    cv2.rectangle(frame, (boundary_box_detection[0], boundary_box_detection[1]), (boundary_box_detection[0] + boundary_box_detection[2], boundary_box_detection[1] + boundary_box_detection[3]), (0, 255, 0), 2)
                    cv2.putText(frame,f"ID: {face_pair}",(boundary_box_detection[0], boundary_box_detection[1] + self.text_offset),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        for id_tracker in list(self.currently_noted.keys()):
            self.unfilled[id_tracker]=self.unfilled[id_tracker]+1
            if self.unfilled[id_tracker]>=45:
                del self.currently_noted[id_tracker]
                self.id_options.append(id_tracker)

        if self.start==0:
            self.start=time.time()
        current=time.time()
        self.end=current-self.start
        if self.end>=5:
            print("Hi")
            self.test=0
            self.currently_seen=list(self.currently_noted.keys())
            while self.currently_seen:
                # start1=time.time()
                self.target=random.choice(self.currently_seen)
                if self.target!=self.previous1 and self.target!=self.previous2:
                    self.x_target, self.y_target=self.currently_noted[self.target]
                    print(f"ID: {self.target}, X: {self.x_target}, Y: {self.y_target}")
                    self.test=1
                if (time.time()-self.start>=1):
                    break

            self.previous2=self.previous1
            self.previous1=self.target
            self.start=0
            self.end=0

            for final_id in list(self.currently_noted.keys()):
                if final_id==self.target:
                    self.final_target=self.target
                    if self.box_state[final_id]:
                        self.in_box=self.box_state[final_id]
                        print(self.in_box)
                    self.x_target_final=self.x_target
                    self.y_target_final=self.y_target
                else:
                    break

        cv2.imshow('face', frame)

video_capture=cv2.VideoCapture(0)
tracker=FaceTracker(video_capture)

while True:
    tracker.process()

    if cv2.waitKey(5) & 0xFF==ord('x'):
        break

video_capture.release()
cv2.destroyAllWindows()
