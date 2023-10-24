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

from voice_player import AudioPlayer

# Set your audio file paths here.  Must correspond to built audio_data.csv!
audio_files = [
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/introduction.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/afraid-of.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/booberry-joke.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/can-i-have-candy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/day-i-was-born.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/did-i-surprise.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/enjoy-halloween.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/favorite-candy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/i-have-scary-story.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/scary-movies.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/simon-says.wav"
]

#example of split between personal and group lines
personal_lines = [0, 1, 2]
group_lines = [3, 4, 5]
creepy_lines = [6, 7, 8]

audio_player = AudioPlayer()

video_capture = cv2.VideoCapture(0)
tracker = FaceTracker(video_capture)
controller = MotionController()

delta_time = 0.02 #time in seconds per frame
diff_time = 0.02
target_wait = random.randrange(3,11)
target_timer = 0
no_face_wait = 3.0 #wait this many seconds before moving back to neutral position
no_face_timer = 0
voice_line_timer = 0
voice_line_wait = 3.0
voice_line_id = 0
voice_line_index = 0

x_deg_neck = Value('d', 0)
y_deg_neck = Value('d', 0)
x_deg_eyes = Value('d', 0)
y_deg_eyes = Value('d', 0)
rehome = Value('b', False)
jaw_scaling = 25

def update_motion(x_deg_neck, y_deg_neck, x_deg_eyes, y_deg_eyes,):
    
    while(True):
        initial_time = timer()
        
        if(rehome.value):
            #print(controller.servo_neck_r.get_pos())
            y_deg_neck.value = controller.pitch_neutral_pos - controller.servo_neck_r.get_pos()#neutral y
            y_deg_eyes.value = controller.pitch_neutral_pos - controller.servo_neck_r.get_pos()
            x_deg_neck.value = stepper.get_forward_ang()
            x_deg_eyes.value = x_deg_neck.value #eyes will look at same point in horizontal
            #print("no faces detected. moving neck:", y_deg_neck.value)

        controller.look_neck(x_deg_neck.value, y_deg_neck.value)
        controller.look_eyes(x_deg_eyes.value, y_deg_eyes.value)
        controller.feed_motors(delta_time)

        jaw_volume, frame = audio_player.update(delta_time)
        #print(jaw_volume * jaw_scaling)
        #print("frame:", frame, "vol:", jaw_volume)
        controller.set_jaw(jaw_volume * jaw_scaling, delta_time)

        while(timer() - initial_time < delta_time):
            pass

def get_new_line(faces):
    line = 0
    #personal line
    if(faces < 3):
        line = personal_lines[random.randrange(0, len(personal_lines))]
    #add logic for playing a creepy line here
    else:
        line = group_lines[random.randrange(0, len(group_lines))]
    return line

motor_process = Process(target=update_motion, args=(x_deg_neck, y_deg_neck, x_deg_eyes, y_deg_eyes,))
motor_process.start()
time.sleep(0.1)

while True:
    init_time = timer()
    frame = tracker.process()
    cv2.imshow('face', frame) #comment out for performance

    face_cnt = tracker.target_info(tracker.target)[4]
    #print("face count:", face_cnt)
    #print("pygame:", audio_player.check_pygame())

    # update target setpoint for motion controller
    if(face_cnt > 0):
        no_face_timer = 0
        rehome.value = False
        #update target based on timer AND duration of frame
        if(target_timer > target_wait):
            tracker.get_new_target()
            target_timer = 0
            target_wait = random.randrange(3,11)
        
        #print(tracker.target)
        x, y = tracker.target_info(tracker.target)[:2]
        x_deg_neck.value, y_deg_neck.value = screen_to_angle(x, y)
        x_deg_eyes.value, y_deg_eyes.value = x_deg_neck.value, y_deg_neck.value
    else:
        no_face_timer += diff_time
        #look back to forward position after not seeing face for long enough
        if(no_face_timer > no_face_wait):
            rehome.value = True

    '''if(audio_player.running.value == True):
        print("pygame:", audio_player.check_pygame())'''

    #speak every random interval of time
    if(voice_line_timer > voice_line_wait):
        voice_line_timer = 0
        if(audio_player.running.value == True):
            print("voice busy")
            voice_line_wait = random.randrange(5,10)
        else:
            voice_line_wait = random.randrange(10,20)
            print("SPEAKING")
            audio_player.play_audio_file(audio_files, voice_line_id)
            voice_line_id = random.randrange(0, len(audio_files))
    
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        controller.process.terminate()
        break

    diff_time = timer() - init_time #calc time frame lasted
    target_timer += diff_time
    voice_line_timer += diff_time
    #print(voice_line_timer)

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()