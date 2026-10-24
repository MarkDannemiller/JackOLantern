'''Sure, I can write some python code for you using the Custom Tkinter library. Here is what I came up with based on your drawn layout:

Python
AI-generated code. Review and use carefully. More info on FAQ.'''

# Importing the Custom Tkinter library
from customtkinter import *

# Creating the main window
window = CTkFrame(master=None, width=800, height=600, title="Talking Robot Control Panel")
window.pack_propagate(False)

# Creating the top buttons
top_buttons = CTkFrame(master=window, width=800, height=100)
top_buttons.pack(side=TOP, fill=X)

eye_led_button = CTkButton(master=top_buttons, text="EYE LED", width=100, height=100, corner_radius=10)
eye_led_button.pack(side=LEFT, padx=10, pady=10)

sleep_button = CTkButton(master=top_buttons, text="SLEEP", width=100, height=100, corner_radius=10)
sleep_button.pack(side=LEFT, padx=10, pady=10)

home_button = CTkButton(master=top_buttons, text="HOME", width=100, height=100, corner_radius=10)
home_button.pack(side=LEFT, padx=10, pady=10)

switch_target_button = CTkButton(master=top_buttons, text="SWITCH TARGET", width=100, height=100, corner_radius=10)
switch_target_button.pack(side=LEFT, padx=10, pady=10)

awake_button = CTkButton(master=top_buttons, text="AWAKE", width=100, height=100, corner_radius=10)
awake_button.pack(side=LEFT, padx=10, pady=10)

neutral_button = CTkButton(master=top_buttons, text="NEUTRAL", width=100, height=100, corner_radius=10)
neutral_button.pack(side=LEFT, padx=10, pady=10)

# Creating the center panels
center_panels = CTkFrame(master=window, width=800, height=400)
center_panels.pack(side=TOP, fill=BOTH, expand=True)

# Creating the voice line setup panel
voice_line_setup_panel = CTkFrame(master=center_panels, width=200, height=400, title="VOICE LINE SETUP")
voice_line_setup_panel.pack(side=LEFT, fill=Y, padx=10, pady=10)

standard_option = CTkRadioButton(master=voice_line_setup_panel, text="STANDARD", width=200, height=50, corner_radius=10)
standard_option.pack(side=TOP, fill=X, padx=10, pady=10)

creepy_option = CTkRadioButton(master=voice_line_setup_panel, text="CREEPY", width=200, height=50, corner_radius=10)
creepy_option.pack(side=TOP, fill=X, padx=10, pady=10)

halloween_option = CTkRadioButton(master=voice_line_setup_panel, text="HALLOWEEN", width=200, height=50, corner_radius=10)
halloween_option.pack(side=TOP, fill=X, padx=10, pady=10)

custom_option = CTkRadioButton(master=voice_line_setup_panel, text="CUSTOM", width=200, height=50, corner_radius=10)
custom_option.pack(side=TOP, fill=X, padx=10, pady=10)

# Creating the manual voice panel
manual_voice_panel = CTkFrame(master=center_panels, width=400, height=400, title="MANUAL VOICE")
manual_voice_panel.pack(side=LEFT, fill=BOTH, expand=True)

text_input = CTkEntry(master=manual_voice_panel, width=300, height=50, corner_radius=10)
text_input.pack(side=TOP, fill=X, padx=10, pady=10)

send_button = CTkButton(master=manual_voice_panel, text="SEND", width=100, height=50, corner_radius=10)
send_button.pack(side=TOP, fill=X, padx=10, pady=10)

# Creating the motion panel
motion_panel = CTkFrame(master=center_panels, width=200, height=400, title="MOTION")
motion_panel.pack(side=LEFT, fill=Y, padx=10, pady=10)

automatic_option = CTkRadioButton(master=motion_panel, text="AUTOMATIC", width=200, height=50, corner_radius=10)
automatic_option.pack(side=TOP, fill=X, padx=10, pady=10)

inverse_kinematics_option = CTkRadioButton(master=motion_panel, text="INVERSE KINEMATICS", width=200, height=50, corner_radius=10)
inverse_kinematics_option.pack(side=TOP, fill=X, padx=10, pady=10)

neck_pitch_option = CTkRadioButton(master=motion_panel, text="NECK PITCH", width=200, height=50, corner_radius=10)
neck_pitch_option.pack(side=TOP, fill=X, padx=10, pady=10)

jaw_option = CTkRadioButton(master=motion_panel, text="JAW", width=200, height=50, corner_radius=10)
jaw_option.pack(side=TOP, fill=X, padx=10, pady=10)

# Starting the main loop
window.mainloop()


#I hope this code helps you with your project. Please let me know if you have any questions or feedback. 😊