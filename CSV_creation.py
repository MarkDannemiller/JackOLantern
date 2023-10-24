import wave
import audioop
import time
import pygame
import csv
import matplotlib.pyplot as plt
pygame.mixer.init()
def plot_volume_data(data):
    plt.plot(data)
    plt.xlabel('Time')
    plt.ylabel('Volume')
    plt.title('Volume Data Over Time')
    plt.show()
#audio_file = wave.open('C:\\Users\\jwfra\\Desktop\\Lab 2\\test_audio.wav', 'rb')
'''audio_file = [
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/introduction.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/afraid-of.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/booberry-joke.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/can-i-have-candy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/day-i-was-born.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/did-i-surprise.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/enjoy-halloween.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/favorite-candy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/i-have-scary-story.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/scary-movies.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/simon-says.wav"
]'''
audio_file = [
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/introduction.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/best-friend-foxy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/boo-berry-pie.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/day-i-was-born.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/haunting-secret.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/movie-in-theaters.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/my-candy-friend.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines5/cowboy/my-singing-friend.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scary-stories.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spirits-come-out.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/two-knee-fish.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/what-afraid-of.wav",
]

list_1=[]
list_final=[]
interval = 0.05
current=time.time()

#pygame.mixer.music.load('C:\\Users\\jwfra\\Desktop\\Lab 2\\test_audio.wav')
#pygame.mixer.music.play()
for i in audio_file:
    audio_file1=wave.open(i)
    samplewidth=audio_file1.getsampwidth()
    framerate=audio_file1.getframerate()
    print(samplewidth)
    print(framerate)
    chunk=int(framerate*interval)
    while(True):
        audio_data = audio_file1.readframes(chunk)
        if not audio_data:
            list_final.append(list_1)
            list_1=[]
            break
        volume = audioop.rms(audio_data, samplewidth)/8000
        if volume<.05:
            volume=0
        elif volume>.90:
            volume=1
        elif volume<=.90 and volume>.80:
            volume=.85
        elif volume<=.80 and volume>.60:
            volume=.7
        elif volume<=.60 and volume>.45:
            volume=.55
        elif volume<=.45 and volume>.30:
            volume=.4
        elif volume<=.30 and volume>.20:
            volume=.25
        elif volume<=.20:
            volume=.15
        list_1.append(volume)
        print(volume)
        time.sleep(interval)
with open('audio_data.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    #transposed = numpy.array(self.final_list).T.tolist()
    for row in list_final:
        writer.writerow(row)
plot_volume_data(list_final)
audio_file.close()
pygame.mixer.music.stop()
pygame.mixer.quit()
