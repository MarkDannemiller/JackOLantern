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
        
