import pygame.midi as pgm
import time
import tkinter as tk
from tkinter import *


pgm.init()

print (pgm.get_default_input_id())
print("-----------------------")
# print (pgm.get_default_output_id())
print (pgm.get_device_info(0))
print (pgm.get_device_info(1))
print (pgm.get_device_info(2))
print (pgm.get_device_info(3))

try:
    def_midi_device = pgm.Input(2)
    # pgm.Output(2)
    # pgm.Output(3, -1,)
except Exception:
    print("Please make sure your MIDI Devices aren't in use by another program and/or re-plug them")

player = pgm.Output(0)
player.set_instrument(0)

# player.note_on(76, velocity=127)
# player.note_on(71, velocity=127)
# time.sleep(0.17)
# player.note_on(76, velocity=127)
# player.note_on(71, velocity=127)
# time.sleep(0.17)
# player.note_on(76, velocity=127)
# player.note_on(71, velocity=127)
# time.sleep(0.17)
# player.note_on(76, velocity=127)
# player.note_on(71, velocity=127)
# time.sleep(0.2)
# player.note_on(74, velocity=127)
# player.note_on(69, velocity=127)
# time.sleep(0.3)
# player.note_on(74, velocity=127)
# player.note_on(69, velocity=127)
# time.sleep(0.3)
# player.note_on(71, velocity=127)
# player.note_on(67, velocity=127)
# time.sleep(0.35)
# player.note_on(71, velocity=127)
# player.note_on(67, velocity=127)
# time.sleep(0.3)
# player.note_on(74, velocity=127)
# player.note_on(69, velocity=127)
# time.sleep(1)

WIDTH = 775
HEIGHT = 700

def BeginRecord():
    i = 0
    while i < 10000:    
        data = pgm.Input.poll(def_midi_device) #Check if there is data
        print (data)
        if bool(data):
            input = pgm.Input.read(def_midi_device, 1) #Read given data and then take the necessary information out of it
            state = input[0][0][0]
            note = input[0][0][1]
            vel = input[0][0][2]
            if state == 144: #Check the state of the note pressed. 144 = pressed, 128 = released
                player.note_on(note, vel)
                i +=1
                print(note, vel)
            

root = tk.Tk()

root.minsize(800, 725)

canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

label = tk.Label(root, text="Jamcorder v0.1",)
label.config(font=("Courier", 24))
label.pack(side = TOP)
label.place(relx= 0.24, relwidth=0.5, rely=0.03)

frame = tk.Frame(root, bg='grey')
frame.place(relx=0.2, rely=0.1, relwidth=0.6, relheight=0.4)

button = tk.Button(root, text="Begin recording", command = BeginRecord)
button.pack()

root.mainloop()