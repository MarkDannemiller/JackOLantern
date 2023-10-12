import wave
import pyaudio
import numpy
from multiprocessing import Process, Value
chunk=2000

class AudioPlayer:
    def __init__(self):
        self.volume_list = []
        self.p = pyaudio.PyAudio()
        self.iteration11 = Value('i', 0)
        self.volume = Value('d', 0)

    def calculate_volume(self, audio_info):
        if numpy.isnan(audio_info).any():
            vol=0
        else:
            peaks=numpy.where((audio_info[1:-1]>audio_info[:-2])&(audio_info[1:-1]>audio_info[2:]))

            if len(peaks)>0:
                max_peak=numpy.max(audio_info)
                vol=max_peak/10000
                vol=abs(vol)
                if vol>1:
                    vol=1
            else:
                vol=0
        self.iteration11.value=self.iteration11.value+1
        if self.iteration11.value>=5:
            print(vol)
            self.iteration11.value=0
        return vol

    #plays audio and periodically updates current volume
    def play_audio_file(self, audio_file, vol):
        wav = wave.open(audio_file, 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wav.getsampwidth()), channels=wav.getnchannels(), rate=wav.getframerate(), output=True)
        try:
            iteration = 0
            while True:
                audio_data = wav.readframes(chunk)
                if not audio_data:
                    break

                audio_info = numpy.frombuffer(audio_data, dtype=numpy.int16)
                if numpy.isnan(audio_info).any():
                    vol.value = 0
                else:
                    vol.value = self.calculate_volume(audio_info)
                iteration = iteration + 1
                print(vol.value)

                if iteration >= 10:
                    iteration = 0

                stream.write(audio_data)
                #print("Hi")

        finally:
            wav.close()
            stream.stop_stream()
            stream.close()
'''
# Set your audio file paths here
audio_files = [
    "C:\\Users\\jwfra\\Desktop\\Lab 2\\Audio Clips\\test_audio.wav",
    "C:\\Users\\jwfra\\Desktop\\Lab 2\\Audio Clips\\second_test.wav",
    "C:\\Users\\jwfra\\Desktop\\Lab 2\\Audio Clips\\third_test.wav"
]

audio_player = AudioPlayer(audio_files)

while True:
    volume = audio_player.play_audio_files()
'''