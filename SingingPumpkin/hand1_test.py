import pygame

def play_video_with_audio(video_file):
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)

    # Initialize the video
    video = pygame.movie.Movie(video_file)
    video.play()
    
    # Initialize the audio
    pygame.mixer.init()
    pygame.mixer.music.load(video_file)
    pygame.mixer.music.play()

    playing = True

    while playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False

        screen.fill((0, 0, 0))
        screen.blit(video.get_surface(), (0, 0))
        pygame.display.flip()

    video.stop()
    pygame.mixer.music.stop()
    pygame.quit()

# Usage example:
video_file = "your_video.mp4"  # Replace with your video file path
play_video_with_audio(video_file)




























import wave
import pyaudio
import numpy
from gpiozero import AngularServo
import time
left_pin=17
right_pin=18
chunk=1024
start=0
end=0
current=0
flag=0        
        
        

class AudioPlayer:
    def __init__(self, audio_files, servo_movement):
        self.volume_list=[]
        self.servo_movement=servo_movement
        self.audio_files=audio_files
        self.p=pyaudio.PyAudio()
    def calculate_volume(self, audio_info):
        vol=int(numpy.sqrt(numpy.mean(numpy.square(audio_info))))
        if numpy.isnan(vol):
            vol=0
        return vol
    def play_audio_files(self):
        for audio_file in self.audio_files:
            wav=wave.open(audio_file, 'rb')
            stream = self.p.open(format=self.p.get_format_from_width(wav.getsampwidth()), channels=wav.getnchannels(), rate=wav.getframerate(), output=True)
            try:
                iteration = 0
                while True:
                    audio_data = wav.readframes(self.chunk)
                    if not audio_data:
                        break

                    audio_info = numpy.frombuffer(audio_data, dtype=numpy.int16)
                    vol = self.calculate_volume(audio_info)
                    iteration=iteration+1

                    if iteration==10:
                        volume_average = int(numpy.mean(self.volume_list))
                        self.volume_list = []
                        self.servo_movement.movement(volume_average)
                    self.servo_movement.movement(vol)

                    stream.write(audio_data)

            finally:
                wav.close()
                stream.stop_stream()
                stream.close()

class Servo_jaw:
    def __init__(self, left_pin, right_pin):
        self.left_servo = AngularServo(left_pin, min_angle=100, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)
        self.right_servo = AngularServo(right_pin, min_angle=260, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)

    def movement(self, volume):
        if volume < 100:
            self.left_servo.angle = 100
            self.right_servo.angle = 260
        elif 100 <= volume < 200:
            self.left_servo.angle = 120
            self.right_servo.angle = 240
        elif 200 <= volume < 300:
            self.left_servo.angle = 150
            self.right_servo.angle = 210
        else:
            self.left_servo.angle = 180
            self.right_servo.angle = 180


            
            
            
            
            
            
            
            
            
            
servo_movement=Servo_jaw(left_pin, right_pin)
audio_files=["C:\\Users\\user\\Desktop\\test_audio.wav", "C:\\Users\\user\\Desktop\\test1_audio.wav", "C:\\Users\\user\\Desktop\\test2_audio.wav"]
audio_player=AudioPlayer(audio_files, servo_movement)
while True:
    audio_player.play_audio_files()
    while (flag==0)
        if (start==0):
            start=time.time()
            flag=0
        if (time.time()-start>=10):
            flag=1
        















[0000007f3c001090] mmal_xsplitter vout display: Try drm
[0000007f3c6a03b0] drm_vout generic: <<< OpenDrmVout: Fmt=DPV0
[0000007f3c6a03b0] drm_vout generic error: drmu_plane_new_find_type: No plane found for types 0x5


def simulate_click_and_alt_f4(x, y):
    # Simulate a click at the specified coordinates
    subprocess.run(["xdotool", "mousemove", str(x), str(y), "click", "1"])

    # Simulate pressing Alt+F4
    subprocess.run(["xdotool", "keydown", "Alt", "key", "F4", "keyup", "Alt"])



import mediapipe
import cv2
import subprocess
import time
import RPi.GPIO as GPIO
import vlc
#from gpiozero import MotionSensor

#pir = MotionSensor(3)
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands
cam = cv2.VideoCapture(0)
pir_pin=17
GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_pin, GPIO.IN)
index_top=0
index_lower=0
second_top=0
second_lower=0
third_top=0
third_lower=0
fourth_top=0
fourth_lower=0
thumb_top=0
thumb_lower=0
first_finger=0
second_finger=0
third_finger=0
fourth_finger=0
fifth_thumb=0
first_song=0
second_song=0
third_song=0
fourth_song=0
fifth_song=0
counter_tracking1=0
counter_tracking2=0
counter_tracking3=0
counter_tracking4=0
counter_tracking5=0
song=0
active=0
# def pumpkin_on(Path):
#     parameters=['omxplayer', '--orientation=0', '--no-osd', Path]
#     subprocess.Popen(parameters).wait()
def pumpkin_on(Path, song):
    instance=vlc.Instance('--no-xlib')
    display=instance.media_player_new()
    video=instance.media_new(Path)
    display.set_media(video)
    display.set_fullscreen(True)
    #time.sleep(5)
    
    if song==1:
        song_duration=5
    elif song==2:
        song_duration=10
    elif song==3:
        song_duration=15
    elif song==4:
        song_duration=20
    elif song==5:
        song_duration=25
    else:
        song_duration=0
    display.play()
    time.sleep(song_duration)
    display.release()
    
def screen_off():
    subprocess.run(["vcgencmd", "display_power", "0"])
def screen_on():
    subprocess.run(["vcgencmd", "display_power", "1"])
    
    

    
    
with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.1, max_num_hands=1) as hands:
#while True:
    #pir.wait_for_motion()
#     if GPIO.input(pir_pin):
#         cam=cv2.VideoCapture(0)
#         time_active=time.time()
#         active=0
#     if (time.time()-time_active>=10):
#         active=1
#         screen_off()
#         cam.release()
    #while (active!=1)
    while (True):
        ret, frame = cam.read()
        frame1 = cv2.resize(frame, (640, 480))
        frame1=cv2.flip(frame, flipCode=-1)
           
        location = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
           
        if location.multi_hand_landmarks==None:
            first_finger=0
            second_finger=0
            third_finger=0
            fourth_finger=0
            fifth_thumb=0
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking4=0
            counter_tracking5=0
        elif location.multi_hand_landmarks != None:
            for handLandmarks in location.multi_hand_landmarks:
                drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)

                for point in handsModule.HandLandmark:
                      
                    Coordinate_points = handLandmarks.landmark[point]
                    if point==8:
                        index_top=Coordinate_points.y
                    if point==6:
                        index_lower=Coordinate_points.y
                    if point==12:
                        second_top=Coordinate_points.y
                    if point==10:
                        second_lower=Coordinate_points.y
                    if point==16:
                        third_top=Coordinate_points.y
                    if point==14:
                        third_lower=Coordinate_points.y
                    if point==20:

                        fourth_top=Coordinate_points.y
                    if point==18:
                        fourth_lower=Coordinate_points.y
                    if point==4:
                        thumb_top=Coordinate_points.y
                    if point==3:
                        thumb_lower=Coordinate_points.y
                        
                        
        first_finger=0
        second_finger=0
        third_finger=0
        fourth_finger=0
        fifth_thumb=0
        if ((index_top!=0 and index_lower!=0)) and (index_top<index_lower):
            first_finger=1


        if ((second_top!=0 and second_lower!=0)) and (second_top<second_lower):
            second_finger=1


        if ((third_top!=0 and third_lower!=0)) and (third_top<third_lower):
            third_finger=1
           
        
        if ((fourth_top!=0 and fourth_lower!=0)) and (fourth_top<fourth_lower):
            fourth_finger=1
            
            
        if ((thumb_top!=0 and thumb_lower!=0)) and (thumb_top<thumb_lower):
            fifth_thumb=1






        if (first_finger==1 and second_finger==0 and third_finger==0 and fourth_finger==0):
            counter_tracking1=counter_tracking1 + 1
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking4=0
            counter_tracking5=0
            #print(counter_tracking1)
            if (counter_tracking1 >10):
                song=1
                screen_on()
                print("Hi")
                Path = '/home/pumpkin1/Music/testing video.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking1=0
                print( "Song: 1")
                screen_off()
                time.sleep(5)
                song=0
        elif (first_finger==1 and second_finger==1 and third_finger==0 and fourth_finger==0):
            counter_tracking2=counter_tracking2 + 1
            counter_tracking1=0
            counter_tracking3=0
            counter_tracking4=0
            counter_tracking5=0
            #print(counter_tracking2)
            if (counter_tracking2> 20):
                song=2
                screen_on()
                Path = '/home/pumpkin1/Music/testing video.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking2=0
                print( "Song: 2")
                screen_off()
                time.sleep(5)
                song=0
        elif (first_finger==1 and second_finger==1 and third_finger==1 and fourth_finger==0):
            counter_tracking3=counter_tracking3 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking4=0
            counter_tracking5=0
            if (counter_tracking3>100):
                song=3
                screen_on()
                Path = '/home/pumpkin1/Music/blink_audio.wav'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking3=0
                print( "Song: 3")
                screen_off()
                time.sleep(5)
                song=0





        elif (first_finger==1 and second_finger==1 and third_finger==1 and fourth_finger==1):
            counter_tracking4=counter_tracking4 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking5=0
            if (counter_tracking4>100):
                song=4
                screen_on()
                Path = '/home/pumpkin1/Music/blink_audio.wav'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking4=0
                print( "Song: 4")
                screen_off()
                time.sleep(5)
                song=0
        elif (first_finger==0 and second_finger==0 and third_finger==0 and fourth_finger==1):
            counter_tracking5=counter_tracking5 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking4=0
            if (counter_tracking5>100):
                song=5
                screen_on()
                Path = '/home/pumpkin1/Music/blink_audio.wav'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking5=0
                print( "Song: 5")
                screen_off()
                time.sleep(5)
                song=0

#            print("First: " + str(counter_tracking1))
#            print("Second: " + str(counter_tracking2))
#            print("Third: " + str(counter_tracking3))
#            print("Fourth " + str(counter_tracking4))
#            print("Fifth " + str(counter_tracking5))

        cv2.imshow("Frame", frame1);
        key = cv2.waitKey(1) & 0xFF
           
        if key == ord("x"):
            screen_on()
            break

















import mediapipe
import cv2
import subprocess
import time
import RPi.GPIO as GPIO
import vlc
# from PIL import Image
#from gpiozero import MotionSensor
import pygame
#pir = MotionSensor(3)
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands
cam = cv2.VideoCapture(0)
pir_pin=17
GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_pin, GPIO.IN)
index_top=0
index_lower=0
second_top=0
second_lower=0
third_top=0
third_lower=0
fourth_top=0
fourth_lower=0
thumb_top=0
thumb_lower=0
first_finger=0
second_finger=0
third_finger=0
fourth_finger=0
fifth_thumb=0
first_song=0
second_song=0
third_song=0
fourth_song=0
fifth_song=0
counter_tracking1=0
counter_tracking2=0
counter_tracking3=0
counter_tracking4=0
counter_tracking5=0
song=0
active=0
# def pumpkin_on(Path):
#     parameters=['omxplayer', '--orientation=0', '--no-osd', Path]
#     subprocess.Popen(parameters).wait()
def pumpkin_on(Path, song):
#     image_location="blank_screen"
#     image=subprocess.Popen(["feh", "--hide-pointer", "--fullscreen", image_location])
#     image.kill()
#     image_process

#     image=Image.open('blank_screen')
#     image.show()
#     time.sleep(3)
#     image.close()

# #     pygame.init()
#     pygame.mouse.set_visible(False)
#     screen = pygame.display.set_mode(1024, 600)
#     screen.fill((0, 0, 0))
#     pygame.display.update()
#     time.sleep(2)
#     pygame.quit()

    instance=vlc.Instance('--no-xlib')
    display=instance.media_player_new()
    video=instance.media_new(Path)
    display.set_media(video)
    display.set_fullscreen(True)
    #time.sleep(5)
    
    if song==1:
        song_duration=5
    elif song==2:
        song_duration=10
    elif song==3:
        song_duration=15
    elif song==4:
        song_duration=20
    elif song==5:
        song_duration=25
    else:
        song_duration=0
    display.play()
    time.sleep(song_duration)
    display.release()
    
def screen_off():
    subprocess.run(["vcgencmd", "display_power", "0"])
def screen_on():
    subprocess.run(["vcgencmd", "display_power", "1"])
    
    
    

    
    
with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.1, max_num_hands=1) as hands:
#while True:
    #pir.wait_for_motion()
#     if GPIO.input(pir_pin):
#         cam=cv2.VideoCapture(0)
#         time_active=time.time()
#         active=0
#     if (time.time()-time_active>=10):
#         active=1
#         screen_off()
#         cam.release()
    #while (active!=1)
while (pir_no_count<100):
    if (GPIO.input(pir_pin)!=0):
        pir_count=0
    else:
        pir_no_count=pir_count+1
    while (True):
        ret, frame = cam.read()
        frame1 = cv2.resize(frame, (640, 480))
        frame1=cv2.flip(frame, flipCode=-1)
           
        location = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
           
        if location.multi_hand_landmarks==None:
            first_finger=0
            second_finger=0
            third_finger=0
            fourth_finger=0
            fifth_thumb=0
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking4=0
            counter_tracking5=0
        elif location.multi_hand_landmarks != None:
            for handLandmarks in location.multi_hand_landmarks:
                drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)

                for point in handsModule.HandLandmark:
                      
                    Coordinate_points = handLandmarks.landmark[point]
                    if point==8:
                        index_top=Coordinate_points.y
                    if point==6:
                        index_lower=Coordinate_points.y
                    if point==12:
                        second_top=Coordinate_points.y
                    if point==10:
                        second_lower=Coordinate_points.y
                    if point==16:
                        third_top=Coordinate_points.y
                    if point==14:
                        third_lower=Coordinate_points.y
                    if point==20:

                        fourth_top=Coordinate_points.y
                    if point==18:
                        fourth_lower=Coordinate_points.y
                    if point==4:
                        thumb_top=Coordinate_points.y
                    if point==3:
                        thumb_lower=Coordinate_points.y
                        
                        
        first_finger=0
        second_finger=0
        third_finger=0
        fourth_finger=0
        fifth_thumb=0
        if ((index_top!=0 and index_lower!=0)) and (index_top<index_lower):
            first_finger=1


        if ((second_top!=0 and second_lower!=0)) and (second_top<second_lower):
            second_finger=1


        if ((third_top!=0 and third_lower!=0)) and (third_top<third_lower):
            third_finger=1
           
        
        if ((fourth_top!=0 and fourth_lower!=0)) and (fourth_top<fourth_lower):
            fourth_finger=1
            
            
        if ((thumb_top!=0 and thumb_lower!=0)) and (thumb_top<thumb_lower):
            fifth_thumb=1






        if (first_finger==1 and second_finger==0 and third_finger==0 and fourth_finger==0):
            counter_tracking1=counter_tracking1 + 1
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking4=0
            counter_tracking5=0
            #print(counter_tracking1)
            if (counter_tracking1 >10):
                song=1
                #time.sleep(2)
                screen_on()
                print("Hi")
                Path = '/home/pumpkin1/Music/testing video.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking1=0
                print( "Song: 1")
                screen_off()
                time.sleep(5)
                song=0
        elif (first_finger==1 and second_finger==1 and third_finger==0 and fourth_finger==0):
            counter_tracking2=counter_tracking2 + 1
            counter_tracking1=0
            counter_tracking3=0
            counter_tracking4=0
            counter_tracking5=0
            #print(counter_tracking2)
            if (counter_tracking2> 20):
                song=2
                screen_on()
                Path = '/home/pumpkin1/Music/testing video.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking2=0
                print( "Song: 2")
                screen_off()
                time.sleep(5)
                song=0
        elif (first_finger==1 and second_finger==1 and third_finger==1 and fourth_finger==0):
            counter_tracking3=counter_tracking3 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking4=0
            counter_tracking5=0
            if (counter_tracking3>100):
                song=3
                screen_on()
                Path = '/home/pumpkin1/Music/blink_audio.wav'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking3=0
                print( "Song: 3")
                screen_off()
                time.sleep(5)
                song=0





        elif (first_finger==1 and second_finger==1 and third_finger==1 and fourth_finger==1):
            counter_tracking4=counter_tracking4 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking5=0
            if (counter_tracking4>100):
                song=4
                screen_on()
                Path = '/home/pumpkin1/Music/blink_audio.wav'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking4=0
                print( "Song: 4")
                screen_off()
                time.sleep(5)
                song=0
        elif (first_finger==0 and second_finger==0 and third_finger==0 and fourth_finger==1):
            counter_tracking5=counter_tracking5 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking4=0
            if (counter_tracking5>100):
                song=5
                screen_on()
                Path = '/home/pumpkin1/Music/blink_audio.wav'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking5=0
                print( "Song: 5")
                screen_off()
                time.sleep(5)
                song=0

#            print("First: " + str(counter_tracking1))
#            print("Second: " + str(counter_tracking2))
#            print("Third: " + str(counter_tracking3))
#            print("Fourth " + str(counter_tracking4))
#            print("Fifth " + str(counter_tracking5))

        cv2.imshow("Frame", frame1);
        key = cv2.waitKey(1) & 0xFF
           
        if key == ord("x"):
            screen_on()
            break




































import mediapipe
import cv2
import subprocess
import time
import RPi.GPIO as GPIO
import vlc
# from PIL import Image
#from gpiozero import MotionSensor
#import pygame
#pir = MotionSensor(3)
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands
cam = cv2.VideoCapture(0)
pir_pin=17
GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_pin, GPIO.IN)
index_top=0
index_lower=0
second_top=0
second_lower=0
third_top=0
third_lower=0
fourth_top=0
fourth_lower=0
thumb_top=0
thumb_lower=0
first_finger=0
second_finger=0
third_finger=0
fourth_finger=0
fifth_thumb=0
first_song=0
second_song=0
third_song=0
fourth_song=0
fifth_song=0
counter_tracking1=0
counter_tracking2=0
counter_tracking3=0
counter_tracking4=0
counter_tracking5=0
song=0
active=0
# def pumpkin_on(Path):
#     parameters=['omxplayer', '--orientation=0', '--no-osd', Path]
#     subprocess.Popen(parameters).wait()
def pumpkin_on(Path, song):
    #screen_off()
    #image_location="/home/pumpkin2/Music/blank.jpg"
    #image=subprocess.Popen(["feh", "--hide-pointer", "--fullscreen", image_location])
    #time.sleep(3)
    
#     image_process

#     image=Image.open('blank_screen')
#     image.show()
#     time.sleep(3)
#     image.close()

# #     pygame.init()
#     pygame.mouse.set_visible(False)
#     screen = pygame.display.set_mode(1024, 600)
#     screen.fill((0, 0, 0))
#     pygame.display.update()
#     time.sleep(2)
#     pygame.quit()
    time.sleep(1)

    instance=vlc.Instance('--no-xlib', '--vout=xvideo')
    display=instance.media_player_new()
    #display.set_fullscreen(True)
    video=instance.media_new(Path)
    display.set_media(video)
    display.set_fullscreen(True)
    time.sleep(1)
    
    if song==1:
        song_duration=41
    elif song==2:
        song_duration=5
    elif song==3:
        song_duration=42
    elif song==4:
        song_duration=42
    elif song==5:
        song_duration=41
    else:
        song_duration=0
    refresh_check()
    display.play()
    refresh_check()
    time.sleep(song_duration)
    refresh()
    display.release()
    #screen_off
    #image.kill()
def screen_off():
    image_location="/home/pumpkin2/Music/blank.jpg"
    image=subprocess.Popen(["feh", "--hide-pointer", "--fullscreen", image_location])
def refresh():
    try:
        window="feh"
        command=f'xdotool search --name "{window}" windowactivate'
        subprocess.call(["/bin/bash", "-c", command])
    except:
        pass
def refresh_check():
    try:
        window="VLC media player."
        command=f'xdotool search --name "{window}" windowactivate'
        subprocess.call(["/bin/bash", "-c", command])
    except:
        pass
def screen_off_full():
    subprocess.run(["vcgencmd", "display_power", "0"])
def screen_on():
    subprocess.run(["vcgencmd", "display_power", "1"])
    

screen_off()     
with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1) as hands:
#while True:
    #pir.wait_for_motion()
#     if GPIO.input(pir_pin):
#         cam=cv2.VideoCapture(0)
#         time_active=time.time()
#         active=0
#     if (time.time()-time_active>=10):
#         active=1
#         screen_off()
#         cam.release()
    #while (active!=1)
#while (pir_no_count<100):
#    if (GPIO.input(pir_pin)!=0):
#        pir_count=0
#    else:
#        pir_no_count=pir_count+1
    while (True):
        refresh()
        ret, frame = cam.read()
        frame1 = cv2.resize(frame, (640, 480))
        frame1=cv2.flip(frame, flipCode=-1)
           
        location = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
           
        if location.multi_hand_landmarks==None:
            first_finger=0
            second_finger=0
            third_finger=0
            fourth_finger=0
            fifth_thumb=0
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking4=0
            counter_tracking5=0
        elif location.multi_hand_landmarks != None:
            for handLandmarks in location.multi_hand_landmarks:
                drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)

                for point in handsModule.HandLandmark:
                      
                    Coordinate_points = handLandmarks.landmark[point]
                    if point==8:
                        index_top=Coordinate_points.y
                    if point==6:
                        index_lower=Coordinate_points.y
                    if point==12:
                        second_top=Coordinate_points.y
                    if point==10:
                        second_lower=Coordinate_points.y
                    if point==16:
                        third_top=Coordinate_points.y
                    if point==14:
                        third_lower=Coordinate_points.y
                    if point==20:

                        fourth_top=Coordinate_points.y
                    if point==18:
                        fourth_lower=Coordinate_points.y
                    if point==4:
                        thumb_top=Coordinate_points.y
                    if point==3:
                        thumb_lower=Coordinate_points.y
                        
                        
        first_finger=0
        second_finger=0
        third_finger=0
        fourth_finger=0
        fifth_thumb=0
        if ((index_top!=0 and index_lower!=0)) and (index_top<index_lower):
            first_finger=1


        if ((second_top!=0 and second_lower!=0)) and (second_top<second_lower):
            second_finger=1


        if ((third_top!=0 and third_lower!=0)) and (third_top<third_lower):
            third_finger=1
           
        
        if ((fourth_top!=0 and fourth_lower!=0)) and (fourth_top<fourth_lower):
            fourth_finger=1
            
            
        if ((thumb_top!=0 and thumb_lower!=0)) and (thumb_top<thumb_lower):
            fifth_thumb=1






        if (first_finger==1 and second_finger==0 and third_finger==0 and fourth_finger==0):
            counter_tracking1=counter_tracking1 + 1
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking4=0
            counter_tracking5=0
            #print(counter_tracking1)
            if (counter_tracking1 >10):
                song=1
                #time.sleep(2)
                #screen_on()
                print("Hi")
                Path = '/home/pumpkin2/Music/Thriller Final 480.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking1=0
                print( "Song: 1")
                #screen_off()
                time.sleep(5)
                song=0
        elif (first_finger==1 and second_finger==1 and third_finger==0 and fourth_finger==0):
            counter_tracking2=counter_tracking2 + 1
            counter_tracking1=0
            counter_tracking3=0
            counter_tracking4=0
            counter_tracking5=0
            #print(counter_tracking2)
            if (counter_tracking2> 10):
                song=2
                #screen_on()
                Path = '/home/pumpkin2/Music/Werewolves Final 480.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking2=0
                print( "Song: 2")
                #screen_off()
                time.sleep(5)
                song=0
        elif (first_finger==1 and second_finger==1 and third_finger==1 and fourth_finger==0):
            counter_tracking3=counter_tracking3 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking4=0
            counter_tracking5=0
            if (counter_tracking3>10):
                song=3
                #screen_on()
                Path = '/home/pumpkin2/Music/Addams Final 480.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking3=0
                print( "Song: 3")
                #screen_off()
                time.sleep(5)
                song=0





        elif (first_finger==1 and second_finger==1 and third_finger==1 and fourth_finger==1):
            counter_tracking4=counter_tracking4 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking5=0
            if (counter_tracking4>10):
                song=4
                #screen_on()
                Path = '/home/pumpkin2/Music/Ghostbusters Final 480.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking4=0
                print( "Song: 4")
                #screen_off()
                time.sleep(5)
                song=0
        elif (first_finger==0 and second_finger==0 and third_finger==0 and fourth_finger==1):
            counter_tracking5=counter_tracking5 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking4=0
            if (counter_tracking5>10):
                song=5
                #screen_on()
                Path = '/home/pumpkin2/Music/Monster Final 480.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking5=0
                print( "Song: 5")
                #screen_off()
                time.sleep(5)
                song=0

#            print("First: " + str(counter_tracking1))
#            print("Second: " + str(counter_tracking2))
#            print("Third: " + str(counter_tracking3))
#            print("Fourth " + str(counter_tracking4))
#            print("Fifth " + str(counter_tracking5))

        cv2.imshow("Frame", frame1);
        #screen_off
        key = cv2.waitKey(1) & 0xFF
           
        if key == ord("x"):
            screen_on()
            break










    try:
        window = "VLC media player"
        command = f'xdotool search --name "{window}"'
        window_id = subprocess.check_output(["/bin/bash", "-c", command]).decode().strip()

        # Click on the VLC window to bring it to the front
        subprocess.call(["xdotool", "windowactivate", "--sync", window_id])
        
        # Wait for a short time to ensure the window is brought to the front
        time.sleep(1)

        # Send Alt+F11 key press to go full screen
        subprocess.call(["xdotool", "key", "Alt+F11"])
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function to bring VLC to the front and make it full screen
refresh_check()
This code first uses xdotool to find the window ID of the VLC media player window and then uses the windowactivate command to bring it to the front. After a brief delay, it sends the Alt+F11 key press to make it go full screen.




