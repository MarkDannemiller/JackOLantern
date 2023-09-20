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
mediapipe_face_detection = mediapipe.solutions.face_detection
mediapipe_drawing = mediapipe.solutions.drawing_utils
cam = cv2.VideoCapture(0)
face_entered_square = 0
currently_noted = {}
counter_id = 0
id_options = list(range(10))
unfilled={}
text_offset=0
box_state={}
target=0
start=0
end=0
x_target=0
y_target=0
check=1
timer=0
previous1=None
previous2=None
currently_seen=None
test=0
x_target_final=0
y_target_final=0
target_final=0
        
        
        
        
while True:
    ret, frame = cam.read()
    frame = cv2.resize(frame, (640, 480))
    if not ret:
        break
    if (face_entered_square):
        cv2.rectangle(frame, (250, 150), (400, 300), (0, 255, 0), 1)
    face_entered_square = 0
    with mediapipe_face_detection.FaceDetection(model_selection=1, min_detection_confidence=.5) as detector_settings:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = detector_settings.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if results.detections:
            for detection in results.detections:
                face_pair=""
                initial_bounding=detection.location_data.relative_bounding_box
                #height_scale, width_scale, _ = frame.shape
                boundary_box_detection=int(initial_bounding.xmin*640), int(initial_bounding.ymin*480), int(initial_bounding.width*640), int(initial_bounding.height*480)
                x = int(640-initial_bounding.xmin*640)
                y = int(480-initial_bounding.ymin*480)
                if (250<x<400) and (150<y<350):
                    face_entered_square=1

                    
                    
                for id_tracker, (x_comparison, y_comparison) in currently_noted.items():
                    x, y, _, _ =boundary_box_detection
                    if (abs(x-x_comparison)<100) and (abs(y-y_comparison)<100):
                        face_pair=id_tracker
                        unfilled[id_tracker]=0
                        break
                        
                if face_pair != "":
                    unfilled[face_pair] = 0
                    x_comparison, y_comparison = currently_noted[face_pair]
                    jitter_coordinate_x=.9*(boundary_box_detection[0] - x_comparison)+x_comparison
                    jitter_coordinate_y=.9*(boundary_box_detection[1] - y_comparison)+y_comparison
                    currently_noted[face_pair]=(jitter_coordinate_x, jitter_coordinate_y)
                    if face_pair not in box_state:
                        box_state[face_pair] = 0
                    if (250<boundary_box_detection[0]<400) and (150<boundary_box_detection[1]<350):
                        box_state[face_pair] = 1
                    else:
                        box_state[face_pair] = 0
                else:
                    if id_options:
                        face_pair = id_options[0]
                        del id_options[0]
                    else:
                        face_pair = counter_id
                        counter_id += 1
                currently_noted[face_pair] = (boundary_box_detection[0], boundary_box_detection[1])
                unfilled[face_pair] = 0
                text_offset=20
                cv2.rectangle(frame, (boundary_box_detection[0], boundary_box_detection[1]), (boundary_box_detection[0] + boundary_box_detection[2], boundary_box_detection[1] + boundary_box_detection[3]), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {face_pair}", (boundary_box_detection[0], boundary_box_detection[1]+text_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                #print(f"ID: {face_pair}, X: {boundary_box_detection[0]}, Y: {boundary_box_detection[1]}")
    for id_tracker in list(currently_noted.keys()):
        if id_tracker not in unfilled:
            unfilled[id_tracker] = 1
        else:
            unfilled[id_tracker] += 1
            if unfilled[id_tracker] >= 30:
                del currently_noted[id_tracker]
                id_options.append(id_tracker)
    
    
    if (start == 0):
        start = time.time()
    current = time.time()
    end = current - start
    if (end >= 5):
        print("Hi")
        test = 0
        currently_seen = list(currently_noted.keys())
        


        while test == 0:
            target = random.choice(currently_seen)
            if target != previous1 and target != previous2:
                x_target, y_target = currently_noted[target]
                print(f"ID: {target}, X: {x_target}, Y: {y_target}")
                test = 1
            if (time.time() - start >= 1):
                break  # Exit the loop if 10 seconds have passed

        previous2 = previous1
        previous1 = target
        start = 0
        end = 0
        
        
        for final_id in list(currently_noted.keys()):
            if final_id==target:
                final_target=target
                x_target_final=x_target
                y_target_final=y_target
            else:
                break


    
    
        
        
    
    cv2.imshow('face', frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cam.release()
cv2.destroyAllWindows()
