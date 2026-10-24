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
audio_files = [
    #normal lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/introduction.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/boo-berry-pie.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/day-i-was-born.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/haunting-secret.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/movie-in-theaters.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/my-candy-friend.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/my-singing-friend.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scary-stories.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spirits-come-out.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/two-knee-fish.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/a-good-lawyer.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/any-questions.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/candybot.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/i-have-friends.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/i-spy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/make-engineer-cry.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/our-differences.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/normal/songbot.wav",

    #personal lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/what-afraid-of.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/best-friend-foxy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/dont-have-ears.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/favorite-pumpkin.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/gourdish-guy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/howdy-little-one.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/lot-of-candy.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/sofishticated.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/personal/what-afraid-of.wav",

    #group lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/group/guess-the-movie.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/group/hard-of-hearing.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/group/quite-the-group.wav",

    #inviting lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/inviting/come-over.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/inviting/dont-bite.wav",

    #scenario lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/colton-greeting.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/enigma.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/eric-greeting.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/exhausted.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/haustein-man.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/jackson-dad.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/jacob-cant-see.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/logan-greeting.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/sahil-greet.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/starburst-starburst.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/take-a-break.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/tony-greeting.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/scenario/voice-box-issue.wav",

    #spooky lines
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spooky/inner-child.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spooky/my-new-home.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spooky/simon-says.wav",
    "/home/pumpkin1/Desktop/Github/JackOLantern/voice-lines/cowboy/spooky/want-a-human.wav"

]

list_1=[]
list_final=[]
interval = 0.05
current=time.time()

#pygame.mixer.music.load('C:\\Users\\jwfra\\Desktop\\Lab 2\\test_audio.wav')
#pygame.mixer.music.play()
for i in audio_files:
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
audio_files.close()
pygame.mixer.music.stop()
pygame.mixer.quit()
