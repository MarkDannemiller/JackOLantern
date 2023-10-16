import pandas as pd
import time
import pygame
import csv
import audioop
import matplotlib.pyplot as plt
pygame.mixer.init()
def plot_volume_data(data):
    plt.plot(data)
    plt.xlabel('Time')
    plt.ylabel('Volume')
    plt.title('Volume Data Over Time')
    plt.show()
audio_id=0
audio_file = ['C:\\Users\\jwfra\\Desktop\\Lab 2\\test_audio.wav', 'C:\\Users\\jwfra\\Desktop\\Lab 2\\second_test.wav', 'C:\\Users\\jwfra\\Desktop\\Lab 2\\third_test.wav']
pygame.mixer.music.load(audio_file[audio_id])
audio_graph=[]
csv_file = 'audio_data.csv'
with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    iterated_row = None
    for i1, row in enumerate(reader):
        if i1 == audio_id:
            iterated_row = row
            break
pygame.mixer.music.play()
for data in iterated_row:
    current_data = data
    audio_graph.append(current_data)
    print(current_data)
    time.sleep(0.1)
plot_volume_data(audio_graph)
pygame.mixer.music.stop()
pygame.mixer.quit()
