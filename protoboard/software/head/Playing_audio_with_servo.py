import pandas
import csv
import time
import numpy as np
import pygame

while (1): #I threw it in a while loop just to make sure the quit and unload worked
    pygame.mixer.init()
    audio_file = '/home/pumpkin1/Music/test_audio.wav' #Wherever you have your stored files would be this input
    pygame.mixer.music.load(audio_file)
    csv_file = 'audio_data.csv' #This is the csv for all audio (depending on which audio_id sent to the code, it will select the respective columns data)
    #audio_data=pandas.read_csv(csv_file, header=None, dtype=np.float64)
    
    audio_data = []

    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            print(', '.join(row))
            audio_data.append(row)

    audio_id = 0 #determined somewhere else (probably make your dictionary with the keys being the ids and their content being the file path, have the audio_id passed in and then used to select the file path)
    selected_row = audio_data[audio_id]
    print(selected_row) #Just for testing, can be removed
    time.sleep(1)
    pygame.mixer.music.play() #will begin audio
    #print(pygame.mixer.music.get_busy())
    for i in selected_row: #the for loop collects a new value from the list every .5 seconds (same interval the csv collects from)
        current_movement=i
        print(current_movement) #just for testing
        time.sleep(.5) #determines the time interval
    #print(pygame.mixer.music.get_busy())
    #Be careful with get_busy as it seems to not be perfectly instataneous (pretty close though, good for error corrections if they arise)
    
    #The get busy commadsd returns a true or false depending on if the audio is still playing, maybe just a statement that says break from assigning values if it is false

    pygame.mixer.music.unload #this command unloads the music, I do not know if needed, maybe only if performance is an issue
    pygame.mixer.quit()