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
    #normal lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/introduction.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/boo-berry-pie.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/day-i-was-born.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/haunting-secret.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/movie-in-theaters.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/my-candy-friend.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/my-singing-friend.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scary-stories.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spirits-come-out.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/two-knee-fish.wav", #9
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/a-good-lawyer.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/any-questions.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/candybot.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/i-have-friends.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/i-spy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/make-engineer-cry.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/our-differences.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/songbot.wav",
    #index 18 ->
    #personal lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/what-afraid-of.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/best-friend-foxy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/dont-have-ears.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/favorite-pumpkin.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/gourdish-guy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/howdy-little-one.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/lot-of-candy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/sofishticated.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/what-afraid-of.wav",
    #index 27->
    #group lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/group/guess-the-movie.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/group/hard-of-hearing.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/group/quite-the-group.wav",
    #index 30->
    #inviting lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/inviting/come-over.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/inviting/dont-bite.wav",
    #index 32->
    #scenario lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/colton-greeting.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/enigma.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/eric-greeting.wav", #34
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/exhausted.wav", #35
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/haustein-man.wav", #36
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/jackson-dad.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/jacob-cant-see.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/logan-greeting.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/sahil-greet.wav", #40
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/starburst-starburst.wav", #41
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/take-a-break.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/tony-greeting.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/voice-box-issue.wav",
    #index 45->
    #spooky lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spooky/inner-child.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spooky/my-new-home.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spooky/simon-says.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spooky/want-a-human.wav"

]

#example of split between personal and group lines
personal_lines = [18,19,20,21,22,23,24,25,26]
group_lines = [27,28,29]
inviting_lines = [30,31] #implement! currently just acts like normal lines
scenario_lines = [32,33,34,35,36,37,38,39,40,41,42,43,44] #lines that will be specifically called by user outside of facial recognition
spooky_lines = [45,46,47,48]

NORMAL = 0
FORCE_GROUP = 1
INCLUDE_SPOOKY = 2
CREEPY_ONLY = 3
#DRUNK = 4
voice_mode = NORMAL

#CHARACTER MODE DETERMINES BEHAVIOR
SLEEP = -1
IDLE = 0
GROUP = 1
PERSONAL = 2
character_mode = Value('i', IDLE)

voice_history = [0]
history_count = 10 #do not speak the last this many lines
personal_face_size = 80 #play personal voice line if current face is this size
far_face_size = 20 #if this size is detected, will call out to person to come over

audio_player = AudioPlayer()

video_capture = cv2.VideoCapture(0)
tracker = FaceTracker(video_capture)
controller = MotionController()

delta_time = 0.02 #time in seconds per frame
diff_time = 0.02
target_wait = random.randrange(3,11)
target_timer = 0
no_face_wait = 3.0 #wait this many seconds before moving back to neutral position
sleep_wait = 60.0 #time to wait before sleeping
no_face_timer = 0
voice_line_timer = 0
voice_line_wait = 3.0
voice_line_id = 44#0#//34=Haustein//////44=vb issue////////47-simon/////////////////////////////
voice_line_index = 0

x_deg_neck = Value('d', 0)
y_deg_neck = Value('d', 0)
x_deg_eyes = Value('d', 0)
y_deg_eyes = Value('d', 0)
face_size = Value('i', 10)
rehome = Value('b', False)
jaw_scaling = 25

def update_motion(x_deg_neck, y_deg_neck, x_deg_eyes, y_deg_eyes,):
    
    while(True):
        initial_time = timer()

        #check for sleep mode
        if(character_mode.value == SLEEP):
            controller.sleep()
            controller.feed_motors(delta_time)
        else:      
            if(rehome.value):
                #print(controller.servo_neck_r.get_pos())
                y_deg_neck.value = controller.pitch_neutral_pos - controller.servo_neck_r.get_pos()#neutral y
                y_deg_eyes.value = controller.pitch_neutral_pos - controller.servo_neck_r.get_pos()
                x_deg_neck.value = stepper.get_forward_ang()
                x_deg_eyes.value = 0#x_deg_neck.value #eyes will look at same point in horizontal
                face_size.value = 0
                #print("no faces detected. moving neck:", y_deg_neck.value)

            controller.look_neck(x_deg_neck.value, y_deg_neck.value)
            controller.look_eyes(x_deg_eyes.value, y_deg_eyes.value, face_size.value)
            controller.feed_motors(delta_time)

            jaw_volume, frame = audio_player.update(delta_time)
            #print(jaw_volume * jaw_scaling)
            #print("frame:", frame, "vol:", jaw_volume)
            controller.set_jaw(jaw_volume * jaw_scaling, delta_time)

        while(timer() - initial_time < delta_time):
            #print(timer() - initial_time)
            pass

def get_new_line(face_count, face_size):
    line = -1
    #personal line
    if(voice_mode != FORCE_GROUP and (face_count < 3 or face_size >= personal_face_size)):
        print("Selecting personal line...")
        while(line == -1 or line in voice_history or line in group_lines or line in scenario_lines or (line in spooky_lines and voice_mode != INCLUDE_SPOOKY)):
            print(line)
            line = random.randrange(0, len(audio_files))
    #add logic for playing a creepy line here
    else:
        print("Selecting group line...")
        while(line == -1 or line in voice_history or line in personal_lines or line in scenario_lines or (line in spooky_lines and voice_mode != INCLUDE_SPOOKY)):
            print(line)
            line = random.randrange(0, len(audio_files))
    voice_history.append(voice_line_id)
    #only keep 10 lines in history/memory, otherwise choose random line
    print("voice history:", voice_history)
    if(len(voice_history) > history_count):
        voice_history.remove(voice_history[0])
    print("line selected:", line)
    return line

def play_line_manual(line):
            voice_line_wait = 1  #immediately speak after current line completes
            voice_history.remove(voice_line_id) #remove currently selected next line
            voice_line_id = line
            voice_history.append(voice_line_id) #replaces next line with manual line

motor_process = Process(target=update_motion, args=(x_deg_neck, y_deg_neck, x_deg_eyes, y_deg_eyes,))
motor_process.start()
time.sleep(0.1)

while True:
    init_time = timer()
    frame = tracker.process()
    cv2.imshow('face', frame) #comment out for performance

    x, y, w, h, face_cnt, box = tracker.target_info(tracker.target)
    #print("face count:", face_cnt)
    #print("pygame:", audio_player.check_pygame())

    # update target setpoint for motion controller
    if(face_cnt > 0):
        no_face_timer = 0
        
        #leave sleep if sleeping
        if(character_mode.value == SLEEP):
            print("Awaking from sleep...")
            character_mode.value = IDLE
        #update target based on timer AND duration of frame
        if(target_timer > target_wait or rehome.value):
            tracker.get_new_target()
            target_timer = 0
            target_wait = random.randrange(2,5)

        rehome.value = False
        face_size.value = int((w + h) / 2) #calc face_size as average of width and height

        #print(face_size.value)
        #print(tracker.target)
        x_deg_neck.value, y_deg_neck.value = screen_to_angle(x, y)
        x_deg_eyes.value, y_deg_eyes.value = x_deg_neck.value, y_deg_neck.value
    else:
        print("no one seen for", no_face_timer, "seconds")
        no_face_timer += diff_time
        #look back to forward position after not seeing face for long enough
        if(no_face_timer > sleep_wait and audio_player.running.value == False):
            print("ENTERING SLEEP MODE...")
            character_mode.value = SLEEP
        elif(no_face_timer > no_face_wait and not rehome.value):
            print("No humans detected.  Rehoming...")
            rehome.value = True

    '''if(audio_player.running.value == True):
        print("pygame:", audio_player.check_pygame())'''

    #speak every random interval of time
    if(voice_line_timer > voice_line_wait and character_mode.value != SLEEP):
        voice_line_timer = 0
        if(audio_player.running.value == True):
            print("voice busy")
        else:
            if(face_cnt>0):
                voice_line_wait = random.randrange(2, 5)
            else:
                voice_line_wait = random.randrange(5,10)
            print("SPEAKING")
            audio_player.play_audio_file(audio_files, voice_line_id)
            voice_line_id = get_new_line(face_cnt, face_size.value)
    
    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        controller.process.terminate()
        break

    diff_time = timer() - init_time #calc time frame lasted
    target_timer += diff_time

    #increment timer if not currently speaking
    if(not audio_player.running.value):
        voice_line_timer += diff_time
    #print(diff_time)
    #print(rehome.value)
    #print(voice_line_timer)

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()