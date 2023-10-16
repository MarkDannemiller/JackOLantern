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
audio_file = ['C:\\Users\\jwfra\\Desktop\\Lab 2\\test_audio.wav', 'C:\\Users\\jwfra\\Desktop\\Lab 2\\second_test.wav', 'C:\\Users\\jwfra\\Desktop\\Lab 2\\untitled.wav']
list_1=[]
list_final=[]
interval = 0.1
current=time.time()

pygame.mixer.music.load('C:\\Users\\jwfra\\Desktop\\Lab 2\\test_audio.wav')
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
        volume = audioop.rms(audio_data, samplewidth)/3000
        if volume<.05:
            volume=0
        elif volume>.90:
            volume=1
        elif volume<=.90 and volume>.80:
            volume=.85
        elif volume<=.80 and volume>.60:
            volume=.75
        elif volume<=.60 and volume>.45:
            volume=.65
        elif volume<=.45 and volume>.30:
            volume=.55
        elif volume<=.30 and volume>.20:
            volume=.40
        elif volume<=.20:
            volume=.25
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
