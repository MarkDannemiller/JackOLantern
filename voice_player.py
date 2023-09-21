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
        if numpy.isnan(numpy.sqrt(numpy.mean(numpy.square(audio_info)))).any():
            vol=0
        else:
            vol=numpy.sqrt(numpy.mean(numpy.square(audio_info)))
        return vol
    def play_audio_files(self):
        for audio_file in self.audio_files:
            wav=wave.open(audio_file, 'rb')
            stream = self.p.open(format=self.p.get_format_from_width(wav.getsampwidth()), channels=wav.getnchannels(), rate=wav.getframerate(), output=True)
            try:
                iteration = 0
                while True:
                    audio_data = wav.readframes(chunk)
                    if not audio_data:
                        break

                    audio_info = numpy.frombuffer(audio_data, dtype=numpy.int16)
                    if numpy.isnan(audio_info).any():
                        vol = 0
                    else:
                        vol = self.calculate_volume(audio_info)
                    iteration=iteration+1

                    if iteration==10:
                        if numpy.isnan(self.volume_list).any():
                            volume_average=0
                            self.volume_list = []
                            self.servo_movement.movement(volume_average)
                        else:
                            volume_average=numpy.mean(self.volume_list)
                            self.volume_list=[]
                            self.servo_movement.movement(volume_average)
                    self.servo_movement.movement(vol)

                    stream.write(audio_data)

            finally:
                wav.close()
                stream.stop_stream()
                stream.close()

class Servo_jaw:
    def __init__(self, left_pin, right_pin):
        self.left_servo = AngularServo(left_pin, min_angle=0, max_angle=270, min_pulse_width=0.0005, max_pulse_width=0.0025)
        self.right_servo = AngularServo(right_pin, min_angle=0, max_angle=270, min_pulse_width=0.0005, max_pulse_width=0.0025)

    def movement(self, volume):
        if volume < 20:
            self.left_servo.angle = 100
            self.right_servo.angle = 260
        elif 20 <= volume < 35:
            self.left_servo.angle = 120
            self.right_servo.angle = 240
        elif 35 <= volume < 45:
            self.left_servo.angle = 150
            self.right_servo.angle = 210
        else:
            self.left_servo.angle = 180
            self.right_servo.angle = 180


            
            
            
            
            
            
            
            
            
            
servo_movement=Servo_jaw(left_pin, right_pin)
audio_files=["C:\\Users\\user\\Desktop\\test_audio.wav", "C:\\Users\\user\\Desktop\\second_test.wav", "C:\\Users\\user\\Desktop\\third_test.wav"]
audio_player=AudioPlayer(audio_files, servo_movement)
while True:
    audio_player.play_audio_files()
    while (flag==0):
        if (start==0):
            start=time.time()
            flag=0
        if (time.time()-start>=10):
            flag=1















import mediapipe
import cv2
import subprocess
import time
#from gpiozero import MotionSensor

#pir = MotionSensor(3)
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands
cam = cv2.VideoCapture(0)
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
# def pumpkin_on(Path):
#     parameters=['omxplayer', '--orientation=0', '--no-osd', Path]
#     subprocess.Popen(parameters).wait()
# def screen_off():
#     subprocess.run(["vcgencmd", "display_power", "0"])
# def screen_on():
#     subprocess.run(["vcgencmd", "display_power", "1"])
    
    

    
    
with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.1, max_num_hands=1) as hands:
#while True:
    #pir.wait_for_motion()
    while (True):
        ret, frame = cam.read()
        frame1 = cv2.resize(frame, (640, 480))
           
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
            if (counter_tracking1 >100):
#                   screen_on()
#                   Path = 'first_video.mp4'
#                   pumpkin_on(Path)
                first_song=1
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking1=0
                print( "Song: 1")
#                     screen_off()
        elif (first_finger==1 and second_finger==1 and third_finger==0 and fourth_finger==0):
            counter_tracking2=counter_tracking2 + 1
            counter_tracking1=0
            counter_tracking3=0
            counter_tracking4=0
            counter_tracking5=0
            if (counter_tracking2> 100):
#                     screen_on()
#                     Path = 'second_video.mp4'
#                     pumpkin_on(Path)
                first_song=0
                second_song=1
                third_song=0
                fourth_song=0
                fifth_song=0
                counter_tracking2=0
                print( "Song: 2")
#                     screen_off()
        elif (first_finger==1 and second_finger==1 and third_finger==1 and fourth_finger==0):
            counter_tracking3=counter_tracking3 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking4=0
            counter_tracking5=0
            if (counter_tracking3>100):
#                     screen_on()
#                     Path = 'third_video.mp4'
#                     pumpkin_on(Path)
                first_song=0
                second_song=0
                third_song=1
                fourth_song=0
                fifth_song=0
                counter_tracking3=0
                print( "Song: 3")
#                     screen_off()





        elif (first_finger==1 and second_finger==1 and third_finger==1 and fourth_finger==1):
            counter_tracking4=counter_tracking4 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking5=0
            if (counter_tracking4>100):
#                     screen_on()
#                     Path = 'fourth_video.mp4'
#                     pumpkin_on(Path)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=1
                fifth_song=0
                counter_tracking4=0
                print( "Song: 4")
#                     screen_off()
        elif (first_finger==0 and second_finger==0 and third_finger==0 and fourth_finger==1):
            counter_tracking5=counter_tracking5 + 1
            counter_tracking1=0
            counter_tracking2=0
            counter_tracking3=0
            counter_tracking4=0
            if (counter_tracking5>100):
#                     screen_on()
#                     Path = 'fifth_video.mp4'
#                     pumpkin_on(Path)
                first_song=0
                second_song=0
                third_song=0
                fourth_song=0
                fifth_song=1
                counter_tracking5=0
                print( "Song: 5")
#                     screen_off()

#            screen_off()
#            print("First: " + str(counter_tracking1))
#            print("Second: " + str(counter_tracking2))
#            print("Third: " + str(counter_tracking3))
#            print("Fourth " + str(counter_tracking4))
#            print("Fifth " + str(counter_tracking5))

        cv2.imshow("Frame", frame1);
        key = cv2.waitKey(1) & 0xFF
           
        if key == ord("x"):
            break
