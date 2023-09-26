import wave
import pyaudio
import numpy

from os import system
import time
left_pin=14
right_pin=15
chunk=1024
start=0
end=0
current=0
flag=0            
        
    

class AudioPlayer:
    def __init__(self, audio_files):
        self.volume_list=[]
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
        print(vol)
                
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
                        

                    stream.write(audio_data)

            finally:
                wav.close()
                stream.stop_stream()
                stream.close()


            
audio_files=["/home/pumpkin1/Music/second_test.wav", "/home/pumpkin1/Music/second_test.wav", "/home/pumpkin1/Music/third_test.wav"]
audio_player=AudioPlayer(audio_files)
while True:
    volume=audio_player.play_audio_files()
    print(volume)

        
