import wave
import pyaudio
import numpy
import time
import csv
import sys

chunk = 375

class AudioPlayer:
    def __init__(self, audio_file_mapping):
        self.volume_check = time.time()
        self.volume_list = []
        self.audio_file_mapping = audio_file_mapping
        self.p = pyaudio.PyAudio()
        self.iteration11 = 0
        self.check = 0
        self.list=[]
        self.final_list=[]

    def calculate_volume(self, audio_info, audio_id):
        if numpy.isnan(audio_info).any():
            vol = 0
        else:
            peaks = numpy.where((audio_info[1:-1] > audio_info[:-2]) & (audio_info[1:-1] > audio_info[2:]))

            if time.time() - self.volume_check >= 0.1: #change to modify timings
                max_peak = numpy.max(audio_info)
                vol = max_peak / 10000
                vol = abs(vol)
                if vol > 1:
                    vol = 1
                self.volume_check = time.time()
                self.list.append(vol)
            else:
                vol = 0
        return vol, self.list

    def play_audio_files(self):
        for audio_file, audio_id in self.audio_file_mapping.items():
            #self.list.append(audio_id)

            try:   
                wav = wave.open(audio_file, 'rb')
                if wav:
                    stream = self.p.open(format=self.p.get_format_from_width(wav.getsampwidth()), channels=wav.getnchannels(), rate=wav.getframerate(), output=True)
                    try:
                        while True:
                            audio_data = wav.readframes(chunk)
                            if not audio_data:
                                break

                            audio_info = numpy.frombuffer(audio_data, dtype=numpy.int16)
                            if numpy.isnan(audio_info).any():
                                vol = 0
                            else:
                                vol = self.calculate_volume(audio_info, audio_id)
                            stream.write(audio_data)

                    finally:
                        print(self.list)
                        self.final_list.append(self.list)
                        print(self.final_list)
                        wav.close()
                        stream.stop_stream()
                        stream.close()
                        self.list=[]
                else:
                    break
            except:
                with open('audio_data.csv', 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    #transposed = numpy.array(self.final_list).T.tolist()
                    for row in self.final_list:
                        writer.writerow(row)
                sys.exit()

#on jacob's computer
'''file_id_mapping = {
    "C:\\Users\\jwfra\\Desktop\\Lab 2\\wave_test.wav": 0,
    "C:\\Users\\jwfra\\Desktop\\Lab 2\\wave_test1.wav": 1,
    "C:\\Users\\jwfra\\Desktop\\Lab 2\\wave_test2.wav": 2,
    "C:\\Users\\jwfra\\Desktop\\Lab": 4
}'''

#on pi
file_id_mapping = {
    "/home/pumpkin1/Music/test_audio.wav": 0,
    "/home/pumpkin1/Music/second_test.wav": 1,
    "/home/pumpkin1/Music/third_test.wav": 2,
    "/home/pumpkin1/Music/": 4
}

audio_player = AudioPlayer(file_id_mapping)

while True:
    volume = audio_player.play_audio_files()

