# -*- coding: utf-8 -*-
import pygame.midi

pygame.init()
pygame.midi.init()
input_id = pygame.midi.get_default_input_id()
print("input MIDI:%d" % input_id)
i = pygame.midi.Input(input_id)

print ("starting")
print ("full midi_events:[[[status,data1,data2,data3],timestamp],...]")

going = True
count = 0
while going:
    if i.poll():
        midi_events = i.read(10)
        print ("full midi_events:" + str(midi_events) )
        count += 1
    if count >= 14:
        going = False

i.close()
pygame.midi.quit()
pygame.quit()
exit()