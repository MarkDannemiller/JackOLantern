import wave
import pyaudio
import numpy
from gpiozero import Servo
import time
from gpiozero.pins.pigpio import PiGPIOFactory
factory=PiGPIOFactory()
left_pin=14
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

                    if iteration==15:
                        iteration=0
                        if numpy.isnan(self.volume_list).any():
                            volume_average=0
                            self.volume_list = []
                            self.servo_movement.movement(volume_average)
                        else:
                            volume_average=numpy.mean(self.volume_list[0])
                            self.volume_list=[]
                            self.servo_movement.movement(volume_average)
                        #print("Hi")
                        
                        self.servo_movement.movement(vol)

                    stream.write(audio_data)

            finally:
                wav.close()
                stream.stop_stream()
                stream.close()

class Servo_jaw:
    def __init__(self):
        self.servo=Servo(14, min_pulse_width=.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
        #self.right_servo = AngularServo(right_pin, min_angle=0, max_angle=270, min_pulse_width=0.0005, max_pulse_width=0.0025)

    def movement(self, volume):
        if numpy.isnan(volume):
            volume=0
            volume=volume/180
            print(volume)
            self.servo.value = volume
        else:
            volume=0
            volume=volume/180
            print(volume)
            self.servo.value = volume
            #self.right_servo.angle = 260
            #print(volume)
        
            
            
            
            
            
            
            
            
            
servo_movement=Servo_jaw()
audio_files=["/home/pumpkin1/Music/blink_audio.wav", "/home/pumpkin1/Music/second_test.wav", "/home/pumpkin1/Music/third_test.wav"]
audio_player=AudioPlayer(audio_files, servo_movement)
while True:
    audio_player.play_audio_files()
    while (flag==0):
        if (start==0):
            start=time.time()
            flag=0
        if (time.time()-start>=10):
            flag=1
        
