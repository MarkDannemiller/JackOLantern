import csv
import pygame

from multiprocessing import Process, Value

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.frame_timer = Value('d', 0)
        self.frame_interval = 0.05
        self.audio_data = []
        self.running = Value('b', False)

        self.speak_delay = 0.8
        
        csv_file = '/home/pumpkin1/Desktop/Github/JackOLantern/audio_data.csv' #This is the csv for all audio (depending on which audio_id sent to the code, it will select the respective columns data)
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                print(', '.join(row))
                row = [int(x) if x.isdigit() else float(x) for x in row]
                self.audio_data.append(row)
        self.selected_row = Value("i", 0)#self.audio_data[0]

    #updates frame timer and returns current volume at correct time based on time step
    def update(self, delta_time):
        #print("busy:", pygame.mixer.music.get_busy())

        if(self.running.value == True):
            self.frame_timer.value += delta_time
            #self.frame_timer = pygame.mixer.music.getpos() * 0.001
            #print("frame timer:", self.frame_timer.value)
            if(self.frame_timer.value >= 0):
                frame = int(self.frame_timer.value / self.frame_interval)

                #end pygame when finished
                if(frame >= len(self.audio_data[self.selected_row.value])):
                    print("exceeded length of row:", len(self.audio_data[self.selected_row.value]))
                    self.running.value = False
                    return 0, len(self.audio_data[self.selected_row.value])
                        
                vol = self.audio_data[self.selected_row.value][frame]
                return vol, frame
            else:
                return 0, 0
        else:
            return 0, 0
        
    def check_pygame():
        return pygame.mixer.music.get_busy()
    
    #plays audio and begins frame timer for update
    def play_audio_file(self, files, audio_id):
        pygame.mixer.music.load(files[audio_id])


        self.selected_row.value = audio_id
        print("Voice Player speaking:", self.audio_data[self.selected_row.value]) #Just for testing, can be removed
        #print("file length:",len(self.selected_row))
        pygame.mixer.music.play() #will begin audio
        
        #reset timer and set running flag high
        self.frame_timer.value = 0 - self.speak_delay
        self.running.value = True