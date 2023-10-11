import cv2
import mediapipe
import random
import time

fov_horiz = 90 #double check
fov_vert = 67.5 #double check
screen_width = 640
screen_height = 480

#returns angle of position on screen based on parameters above
def screen_to_angle(xpixel, ypixel):
    xdegrees = (xpixel-screen_width/2)/screen_width * fov_horiz
    ydegrees = -(ypixel-screen_height/2)/screen_height * fov_vert
    print("converted x:", xpixel, "y:", ypixel, " -> xd:", xdegrees, "yd:", ydegrees)
    return xdegrees, ydegrees

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
        self.get_new_target()
        
        

    def process(self):
        self.number_of_faces=0
        self.check=0
        ret, frame=self.video_capture.read()#get the frame
        frame=cv2.resize(frame, (640, 480))#resizes frame
        if not ret:
            return

        if self.face_entered_square:#if statement that determines if the face is within the box (sets the region of the box)
            cv2.rectangle(frame, (250, 150), (400, 300), (255, 0, 0), 1)
        self.face_entered_square=0 #resets the face_entered square to allow it to check again

        with self.mediapipe_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.05) as detector_settings:
            #////////////Collects data from the model/////////////
            frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            location=detector_settings.process(frame)
            frame=cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            #////////////////////////////////////////////////////
            #////////////Collects data from the model/////////////
            if location.detections:
                for detection in location.detections:
                    face_pair=""
                    initial_bounding = detection.location_data.relative_bounding_box
                    boundary_box_detection=(int(initial_bounding.xmin * 640),int(initial_bounding.ymin * 480),int(initial_bounding.width * 640),int(initial_bounding.height * 480),)
                    x = int(640-initial_bounding.xmin*640) #scales the bottom left ocrner of the box
                    y = int(480 - initial_bounding.ymin*480)#scales the bottom left ocrner of the box
                    if (250<x<400) and (150<y<350): #determines if a face is in the center and allows the blue box to be shown if it is
                        self.face_entered_square=1

                    for id_tracker, (x_comparison, y_comparison) in self.currently_noted.items(): #this for loop goes through all current faces and compares them to the previous list of faces and checks to see if the current iterated face is the same face as in the previous data.
                        x=boundary_box_detection[0]
                        y=boundary_box_detection[1]
                        if (abs(x-x_comparison)<100) and (abs(y-y_comparison)<100):
                            face_pair=id_tracker#assigns current face to the previous face id (keeps track)
                            self.unfilled[id_tracker]=0
                            break
                            
                            
                            
                    if face_pair!="": #this if statement takes the current faces and reduces the distance between the old and new locations for the id to better track
                        self.unfilled[face_pair]=0
                        x_comparison, y_comparison=self.currently_noted[face_pair]
                        jitter_coordinate_x=0.9*abs(boundary_box_detection[0]-x_comparison)+x_comparison
                        jitter_coordinate_y=0.9*abs(boundary_box_detection[1]-y_comparison)+y_comparison
                        self.currently_noted[face_pair]=(jitter_coordinate_x, jitter_coordinate_y)
                    else:
                        if self.id_options: #removes the face from options
                            face_pair=self.id_options[0]
                            del self.id_options[0]
                    self.currently_noted[face_pair]=(boundary_box_detection[0], boundary_box_detection[1]) #collects x and y information for faces
                    self.currently_noted_dimensions[face_pair]=(boundary_box_detection[2], boundary_box_detection[3])#collects width and height locations
                    self.unfilled[face_pair]=0
                    self.text_offset=20
                    #following two lines are display
                    cv2.rectangle(frame, (boundary_box_detection[0], boundary_box_detection[1]), (boundary_box_detection[0] + boundary_box_detection[2], boundary_box_detection[1] + boundary_box_detection[3]), (0, 255, 0), 2)
                    cv2.putText(frame,f"ID: {face_pair}",(boundary_box_detection[0], boundary_box_detection[1] + self.text_offset),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        for id_tracker in list(self.currently_noted.keys()):#this for loop iterates over the current faces seen and adjusts the number of frames that they have been seen (if they are seen above this is reset to 0)
            self.unfilled[id_tracker]=self.unfilled[id_tracker]+1
            self.number_of_faces=self.number_of_faces+1
            if self.unfilled[id_tracker]>=8: #max number of frames to wait before deleting face
                self.box_state[id_tracker]=0
                del self.currently_noted[id_tracker]
                self.id_options.append(id_tracker)

        cv2.imshow('face', frame) #comment out for performance
    def target_info(self, target):#updates the information for the target id

        self.update_coordinates=list(self.currently_noted.keys())#gets all face ids currently seen
        for face_iteration in range(len(self.update_coordinates)): #iterates through faces

            if self.update_coordinates[face_iteration]==self.target:#if this iteration is the target
                #collects x and y information and converts to the middle of the face as well as collecitng the width and height of the box of the target
                self.x_target1, self.y_target1=self.currently_noted[self.target]
                self.width_target1, self.height_target1=self.currently_noted_dimensions[target]
                self.check=1
                self.x_target1=self.x_target1+.5*self.width_target1
                self.y_target1=self.y_target1+.5*self.height_target1
                #determines if the target is within the box or not
                if (250<self.x_target1<400) and (150<self.y_target1<350):
                    self.in_box=1
                else:
                    self.in_box=0
        return self.x_target1, self.y_target1, self.width_target1, self.height_target1, self.number_of_faces, self.in_box
    #I do not use check for anything but looking for errors when testing the code to make sure it is properly going through areas
    def check_info(self):
        return self.check
    def get_new_target(self):#selects the target id from the ids that are currently seen
        self.test=0
        self.currently_seen=list(self.currently_noted.keys())
        while self.currently_seen and self.test==0:

            self.target=random.choice(self.currently_seen)#randomly picks an id from what is available and will redo the choice if it is a repeat, but if there is only one face, it will eventually choose it
            if self.target!=self.previous1:
                self.x_target, self.y_target=self.currently_noted[self.target]
                self.width, self.height=self.currently_noted_dimensions[self.target]
                #gets preliminary target information
                self.test=1
            elif (self.randomize_target>=10):
                self.x_target, self.y_target=self.currently_noted[self.target]
                self.width, self.height=self.currently_noted_dimensions[self.target]
                #gets preliminary target information
                self.randomize_target=0
                self.test=1
            else:
                self.randomize_target=self.randomize_target+1 #to allow it to eventually pick a target if there is only one

        self.previous2=self.previous1 #these two lines give the option for what it avoids picking on first attempt above for the target
        self.previous1=self.target

        for final_id in list(self.currently_noted.keys()):#this for loop just ensure that the target_final is a valid id
            if final_id==self.target:
                self.target_final=self.target
            else:
                break
        
        
        #I believe this for loop does not do anything anymore, just got moved into def target_info
        self.update_coordinates=list(self.currently_noted.keys())
        for face_iteration in range(len(self.update_coordinates)):
            if self.update_coordinates[face_iteration]==self.target_final:
                self.x_target1, self.y_target1=self.currently_noted[self.target]
                self.width_target1, self.height_target1=self.currently_noted_dimensions[self.target]
                self.check=1
        return self.target
        

