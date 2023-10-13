import wave
import pygame
import numpy
from multiprocessing import Process, Value
chunk=2000

class AudioPlayer:
    def __init__(self):
        self.frame_timer = 0
        self.frame_interval = 0.5
        self.audio_data = []
        self.selected_row = 0
        self.running = False
        
        csv_file = 'audio_data.csv' #This is the csv for all audio (depending on which audio_id sent to the code, it will select the respective columns data)
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                print(', '.join(row))
                self.audio_data.append(row)

    #updates frame timer and returns current volume at correct time based on time step
    def update(self, delta_time):
        self.frame_timer += delta_time
        frame = int(self.frame_timer / self.frame_interval)
        vol = self.selected_row[frame]

        #end pygame when finished
        if(not pygame.mixer.music.get_busy()):
            self.running = False
            pygame.mixer.music.unload #this command unloads the music, I do not know if needed, maybe only if performance is an issue
            pygame.mixer.quit()

        return vol
    
    #plays audio and begins frame timer for update
    def play_audio_file(self, files, audio_id):
        pygame.mixer.init()
        pygame.mixer.music.load(files[audio_id])

        self.selected_row = self.audio_data[audio_id]
        print("Voice Player speaking:", self.selected_row) #Just for testing, can be removed
        pygame.mixer.music.play() #will begin audio
        
        #reset timer and set running flag high
        self.frame_timer = 0
        self.running = True