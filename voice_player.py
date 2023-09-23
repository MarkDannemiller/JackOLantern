import wave
import pyaudio
import numpy as np
from gpiozero import Servo
import time
from gpiozero.pins.pigpio import PiGPIOFactory
factory = PiGPIOFactory()
left_pin = 14
right_pin = 18
servo = Servo(left_pin, pin_factory=factory)

chunk = 1024
audio_files = ["/home/pumpkin1/Music/blink_audio.wav", "/home/pumpkin1/Music/second_test.wav", "/home/pumpkin1/Music/third_test.wav"]

class AudioPlayer:
    def __init__(self, audio_files):
        self.audio_files = audio_files
        self.p = pyaudio.PyAudio()

    def play_audio_file(self, audio_file):
        wav = wave.open(audio_file, 'rb')
        stream = self.p.open(
            format=self.p.get_format_from_width(wav.getsampwidth()),
            channels=wav.getnchannels(),
            rate=wav.getframerate(),
            output=True
        )
        
        try:
            iteration = 0
            volume = 0  # Initialize volume
            while True:
                audio_data = wav.readframes(chunk)
                if not audio_data:
                    break

                audio_info = np.frombuffer(audio_data, dtype=np.int16)
                if not np.isnan(audio_info).any():
                    volume = np.abs(audio_info[10])

                iteration = (iteration + 1) % 15

                if iteration == 0:
                    servo.value = volume/1000

                stream.write(audio_data)

        finally:
            wav.close()
            stream.stop_stream()
            stream.close()

    def play_audio_files(self):
        for audio_file in self.audio_files:
            self.play_audio_file(audio_file)

audio_player = AudioPlayer(audio_files)
while True:
    audio_player.play_audio_files()
    time.sleep(10)
