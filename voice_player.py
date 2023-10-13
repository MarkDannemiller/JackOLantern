import csv
import pygame

from multiprocessing import Process, Value

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.frame_timer = 0
        self.frame_interval = 0.5
        self.audio_data = []
        self.running = Value('b', False)
        
        csv_file = 'audio_data.csv' #This is the csv for all audio (depending on which audio_id sent to the code, it will select the respective columns data)
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                print(', '.join(row))
                row = [int(x) if x.isdigit() else float(x) for x in row]
                self.audio_data.append(row)
        self.selected_row = self.audio_data[0]

    #updates frame timer and returns current volume at correct time based on time step
    def update(self, delta_time):
        self.frame_timer += delta_time
        frame = int(self.frame_timer / self.frame_interval)

        #end pygame when finished
        if(frame > len(self.selected_row)):
            self.running.value = False
            return 0
                
        vol = self.selected_row[frame]
        return vol
    
    #plays audio and begins frame timer for update
    def play_audio_file(self, files, audio_id):
        pygame.mixer.music.load(files[audio_id])

        self.selected_row = self.audio_data[audio_id]
        print("Voice Player speaking:", self.selected_row) #Just for testing, can be removed
        pygame.mixer.music.play() #will begin audio
        
        #reset timer and set running flag high
        self.frame_timer = 0
        self.running.value = True