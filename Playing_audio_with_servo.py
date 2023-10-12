import pandas
import time
audio_file = 'audio_file'
pygame.mixer.music.load(audio_file)
csv_file = 'audio_data.csv'
audio_data=pandas.read_csv(csv_file)
audio_id = 0
selected_column = audio_data.iloc[:, audio_id]
data_list = selected_column.tolist()
print(data_list)
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    for i in data_list:
        current_movement=i
        print(current_movement)
        time.sleep(.5)
pygame.mixer.quit()
