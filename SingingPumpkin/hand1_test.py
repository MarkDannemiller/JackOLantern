import mediapipe
import cv2
import subprocess
import time
import RPi.GPIO as GPIO
import vlc
import pyautogui
import pygame
from pygame import mixer
#subprocess.Popen("unclutter -idle 0.01", shell=True)
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
mixer.init()
pygame.init()
pygame.mixer.init()
song=0
active=0
def pumpkin_on(Path, song):
    if song==1:
        Path_audio='/home/pumpkin2/Music/final/(Audio) Thriller Final (1).wav'
    elif song==2:
        Path_audio='/home/pumpkin2/Music/final/Werewolves_final1.wav'
    elif song==3:
        Path_audio='/home/pumpkin2/Music/final/Addams_Final1.wav'
    elif song==4:
        Path_audio='/home/pumpkin2/Music/final/Ghostbusters_Final1.wav'
    elif song==5:
        Path_audio='/home/pumpkin2/Music/final/Monsters_Final1.wav'
    else:
        pass
    #print(song)

    #refresh_check()
    display=cv2.VideoCapture(Path)
    
    cv2.namedWindow("Video_frame", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Video_frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    pygame.mixer.music.load(Path_audio)
    time_check=0
    time.sleep(1)
    if song==1:
        while(1):
            if (time_check==0):
                pygame.mixer.music.play()
                time_check=1
                #time.sleep(2)
            ret, frame_video=display.read()
            if not ret:
                break
            
            cv2.imshow("Video_frame", frame_video)
            key_video = cv2.waitKey(27) & 0xFF    
            if key_video == ord("q"):
                break
    if song==2:
        while(1):
            if (time_check==0):
                pygame.mixer.music.play()
                time_check=1
                time.sleep(1.9)
            ret, frame_video=display.read()
            if not ret:
                break
            cv2.imshow("Video_frame", frame_video)
            key_video = cv2.waitKey(29) & 0xFF    
            if key_video == ord("q"):
                break
    if song==3:
        while(1):
            if (time_check==0):
                pygame.mixer.music.play()
                time_check=1
                time.sleep(1)
            ret, frame_video=display.read()
            if not ret:
                break
            
            cv2.imshow("Video_frame", frame_video)
            key_video = cv2.waitKey(29) & 0xFF    
            if key_video == ord("q"):
                break
    if song==4:
        while(1):
            if (time_check==0):
                pygame.mixer.music.play()
                time_check=1
                time.sleep(1.3)
            ret, frame_video=display.read()
            if not ret:
                break
            cv2.imshow("Video_frame", frame_video)
            key_video = cv2.waitKey(30) & 0xFF    
            if key_video == ord("q"):
                break
    if song==5:
        while(1):
            if (time_check==0):
                pygame.mixer.music.play()
                time_check=1
                time.sleep(2)
            ret, frame_video=display.read()
            if not ret:
                break
            cv2.imshow("Video_frame", frame_video)
            key_video = cv2.waitKey(29) & 0xFF    
            if key_video == ord("q"):
                break
        
        
        
        
        
        
    pygame.mixer.music.stop()
    #print("Hi")
    #pygame.quit()
    display.release()
    cv2.destroyWindow("Video_frame")
    #cam = cv2.VideoCapture(0)


    refresh()
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
        window="VLC media player"
        command=f'xdotool search --name "{window}" windowactivate'
        subprocess.call(["/bin/bash", "-c", command])
        #time.sleep(1)
        #pyautogui.hotkey('alt', 'f11')
        #print("good")
        
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
                #print("Hi")
                Path = '/home/pumpkin2/Music/final/Thriller_Final.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking1=0
                #print( "Song: 1")
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
                Path = '/home/pumpkin2/Music/final/Werewolves_1.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking2=0
                #print( "Song: 2")
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
                Path = '/home/pumpkin2/Music/final/Addams_1.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking3=0
                #print( "Song: 3")
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
                Path = '/home/pumpkin2/Music/final/Ghostbusters_1.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking4=0
                #print( "Song: 4")
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
                Path = '/home/pumpkin2/Music/final/Monsters_1.mp4'
                pumpkin_on(Path, song)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking5=0
                #print( "Song: 5")
                #screen_off()
                time.sleep(5)
                song=0


        cv2.imshow("Frame", frame1);
        #screen_off
        key = cv2.waitKey(1) & 0xFF
           
        if key == ord("x"):
            screen_on()
            break
