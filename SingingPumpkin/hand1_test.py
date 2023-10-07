[0000007f3c001090] mmal_xsplitter vout display: Try drm
[0000007f3c6a03b0] drm_vout generic: <<< OpenDrmVout: Fmt=DPV0
[0000007f3c6a03b0] drm_vout generic error: drmu_plane_new_find_type: No plane found for types 0x5






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
