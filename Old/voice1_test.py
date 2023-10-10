import wave
import pyaudio
import numpy

from os import system
system("sudo pigpiod")
from gpiozero import Servo
import time
from gpiozero.pins.pigpio import PiGPIOFactory
factory=PiGPIOFactory()
left_pin=14
right_pin=15
chunk=1024
start=0
end=0
current=0
flag=0        
system("sudo pigpiod")        
        
    

class AudioPlayer:
    def __init__(self, audio_files, servo_movement):
        self.volume_list=[]
        self.servo_movement=servo_movement
        self.audio_files=audio_files
        self.p=pyaudio.PyAudio()
    def calculate_volume(self, audio_info):
        if numpy.isnan(audio_info).any():
            vol=0
        else:
            vol=audio_info[10]
            vol=vol/1500
            if vol>1:
                vol=1
            if vol<-1:
                vol=-1
                
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
                        iteration=0

                        #print("Hi")
                        
                        self.servo_movement.movement(vol)

                    stream.write(audio_data)

            finally:
                wav.close()
                stream.stop_stream()
                stream.close()

class Servo_jaw:
    def __init__(self):
        self.left_servo=Servo(14, min_pulse_width=.5/1000, max_pulse_width=.633/1000, pin_factory=factory)
        self.right_servo=Servo(15, min_pulse_width=.633/1000, max_pulse_width=.766/1000, pin_factory=factory)

    def movement(self, volume):
        volume1=-volume
        volume2=volume


        print (volume)
        self.left_servo.value = volume1
        self.right_servo.value = volume2
            #self.right_servo.angle = 260
            #print(volume)

#1.167 1.833 1.833 2.5          
            
            
servo_movement=Servo_jaw()
audio_files=["/home/pumpkin1/Music/second_test.wav", "/home/pumpkin1/Music/second_test.wav", "/home/pumpkin1/Music/third_test.wav"]
audio_player=AudioPlayer(audio_files, servo_movement)
while True:
    audio_player.play_audio_files()
    while (flag==0):
        if (start==0):
            start=time.time()
            flag=0
        if (time.time()-start>=10):
            flag=1
        