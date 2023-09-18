import wave
import pyaudio
import numpy
from gpiozero import AngularServo
import time

left_pin = 17
right_pin = 18
chunk = 1024
start = 0
end = 0
current = 0
flag = 0


class AudioPlayer:
    def __init__(self, audio_files, servo_movement):
        self.volume_list = []
        self.servo_movement = servo_movement
        self.audio_files = audio_files
        self.p = pyaudio.PyAudio()

    def calculate_volume(self, audio_info):
        try:
            vol = int(numpy.sqrt(numpy.mean(numpy.square(audio_info))))
        except (ValueError, TypeError):
            # Handle exceptions (NaN values) by setting vol to 0
            vol = 0
        return vol

    def play_audio_files(self):
        for audio_file in self.audio_files:
            wav = wave.open(audio_file, 'rb')
            stream = self.p.open(format=self.p.get_format_from_width(wav.getsampwidth()),
                                channels=wav.getnchannels(), rate=wav.getframerate(), output=True)
            try:
                iteration = 0
                while True:
                    audio_data = wav.readframes(chunk)
                    if not audio_data:
                        break

                    audio_info = numpy.frombuffer(audio_data, dtype=numpy.int16)
                    vol = self.calculate_volume(audio_info)
                    iteration = iteration + 1

                    if iteration == 10:
                        volume_average = int(numpy.mean(self.volume_list))
                        self.volume_list = []
                        self.servo_movement.movement(volume_average)
                    self.servo_movement.movement(vol)

                    stream.write(audio_data)

            finally:
                wav.close()
                stream.stop_stream()
                stream.close()


class Servo_jaw:
    def __init__(self, left_pin, right_pin):
        self.left_servo = AngularServo(left_pin, min_angle=100, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)
        self.right_servo = AngularServo(right_pin, min_angle=260, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)

    def movement(self, volume):
        if volume < 100:
            self.left_servo.angle = 100
            self.right_servo.angle = 260
        elif 100 <= volume < 200:
            self.left_servo.angle = 120
            self.right_servo.angle = 240
        elif 200 <= volume < 300:
            self.left_servo.angle = 150
            self.right_servo.angle = 210
        else:
            self.left_servo.angle = 180
            self.right_servo.angle = 180


servo_movement = Servo_jaw(left_pin, right_pin)
audio_files = ["C:\\Users\\user\\Desktop\\test_audio.wav", "C:\\Users\\user\\Desktop\\test1_audio.wav",
               "C:\\Users\\user\\Desktop\\test2_audio.wav"]
audio_player = AudioPlayer(audio_files, servo_movement)
while True:
    audio_player.play_audio_files()
    while (flag == 0):
        if (start == 0):
            start = time.time()
            flag = 0
        if (time.time() - start >= 10):
            flag = 1
