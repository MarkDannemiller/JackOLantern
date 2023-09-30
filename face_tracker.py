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
        self.currently_noted_dimensions={}
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
        self.width=0
        self.height=0
        self.check=1
        self.timer=0
        self.previous1=None
        self.previous2=None
        self.currently_seen=None
        self.test=0
        self.x_target_final=0
        self.y_target_final=0
        self.width_final=0
        self.height_final=0
        self.target_final=0
        self.start1=0
        self.in_box=0
        self.check=0
        self.number_of_faces=0
        self.update_coordinates=[]
        self.randomize_target=0
        self.x_target1=0
        self.y_target1=0
        self.width_target1=0
        self.height_target1=0
        
        

    def process(self):
        self.number_of_faces=0
        self.check=0
        ret, frame=self.video_capture.read()
        frame=cv2.resize(frame, (640, 480))
        if not ret:
            return

        if self.face_entered_square:
            cv2.rectangle(frame, (250, 150), (400, 300), (255, 0, 0), 1)
        self.face_entered_square=0

        with self.mediapipe_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.05) as detector_settings:
            frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
            #frame=cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
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
#                         if face_pair not in self.box_state:
#                             self.box_state[face_pair]=0
                        if (250<boundary_box_detection[0]<400) and (150<boundary_box_detection[1]<350):
                            self.box_state[face_pair]=1
                        else:
                            self.box_state[face_pair]=0
                    else:
                        if self.id_options:
                            face_pair=self.id_options[0]
                            del self.id_options[0]
                    self.currently_noted[face_pair]=(boundary_box_detection[0], boundary_box_detection[1])
                    self.currently_noted_dimensions[face_pair]=(boundary_box_detection[2], boundary_box_detection[3])
                    self.unfilled[face_pair]=0
                    self.text_offset=20
                    cv2.rectangle(frame, (boundary_box_detection[0], boundary_box_detection[1]), (boundary_box_detection[0] + boundary_box_detection[2], boundary_box_detection[1] + boundary_box_detection[3]), (0, 255, 0), 2)
                    cv2.putText(frame,f"ID: {face_pair}",(boundary_box_detection[0], boundary_box_detection[1] + self.text_offset),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        for id_tracker in list(self.currently_noted.keys()):
            self.unfilled[id_tracker]=self.unfilled[id_tracker]+1
            self.number_of_faces=self.number_of_faces+1
            if self.unfilled[id_tracker]>=45:
                self.box_state[id_tracker]=0
                del self.currently_noted[id_tracker]
                self.id_options.append(id_tracker)

        cv2.imshow('face', frame)
    def target_information(self, target):

        self.update_coordinates=list(self.currently_noted.keys())
        for face_iteration in range(len(self.update_coordinates)):

            if self.update_coordinates[face_iteration]==target:
                self.x_target1, self.y_target1=self.currently_noted[target]
                self.width_target1, self.height_target1=self.currently_noted_dimensions[target]
                self.check=1
                self.x_target1=self.x_target1+.5*self.width_target1
                self.y_target1=self.y_target1+.5*self.height_target1
                if (250<self.x_target1<400) and (150<self.y_target1<350):
                    self.in_box=1
                else:
                    self.in_box=0
        return self.x_target1, self.y_target1, self.width_target1, self.height_target1, self.number_of_faces, self.in_box
    def check_information(self):
        return self.check
    def get_new_target(self):
        self.test=0
        self.currently_seen=list(self.currently_noted.keys())
        while self.currently_seen and self.test==0:

            self.target=random.choice(self.currently_seen)
            #print(self.target)
            if self.target!=self.previous1:
                self.x_target, self.y_target=self.currently_noted[self.target]
                self.width, self.height=self.currently_noted_dimensions[self.target]
                #print(f"ID: {self.target}, X: {self.x_target}, Y: {self.y_target}")
                #print(f"ID: {self.target}, W: {self.width}, H: {self.height}")
                self.test=1
                #break
            elif (self.randomize_target>=10):
                self.x_target, self.y_target=self.currently_noted[self.target]
                self.width, self.height=self.currently_noted_dimensions[self.target]
                self.randomize_target=0
                self.test=1
                #break
            else:
                self.randomize_target=self.randomize_target+1

#                 if (time.time()-self.start1>=5):
#                     break

        self.previous2=self.previous1
        self.previous1=self.target

        for final_id in list(self.currently_noted.keys()):
            if final_id==self.target:
                self.target_final=self.target
                self.x_target_final=self.x_target
                self.y_target_final=self.y_target
                self.width_final=self.width
                self.height_final=self.height
                self.check=1
                #time.sleep(2)
            else:
                break

                
        return self.target

        

video_capture=cv2.VideoCapture(0)
tracker=FaceTracker(video_capture)
position_x=0
position_y=0
s=time.time()
e=time.time()
final_id=0
# while True:
#     tracker.process()
#     check=tracker.check_information()
#     #print(check)
#     if (time.time()-e>=6):
#         final_id=tracker.get_new_target()
#         e=time.time()
        
    
#     if time.time()-s>=2:
#         x_location, y_location, width, height, number_of_faces, box=tracker.target_information(final_id)
#         if (width!=0 and number_of_faces!=0):
#             print("x: ", x_location)
#             print("y: ", y_location)
#             print("width: ", width)
#             print("height: ", height)
#             print("target: ", final_id)
#             print("number: ", number_of_faces)
#             print("in box: ", box)
#             print("/////////////////////////")
#         s=time.time()
        

#     if cv2.waitKey(5) & 0xFF==ord('x'):
#         break

video_capture.release()
cv2.destroyAllWindows()
#frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
