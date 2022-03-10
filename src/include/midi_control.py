import sys
import mido
import os
import csv
import time
import datetime
from mido import MidiFile 
from multiprocessing import Process, Value, Array

from include.globals import MIDI_MAX_PAST
from include.globals import MIDI_MAX_FUTURE
from include.globals import MIDI_PLAY_GOOD_HITS
from include.globals import MIDI_PLAY_ALL_HITS
from include.globals import MIDI_PLAY_MIDIFILE_NOTES
from include.globals import JOY_BUFF_SIZE

# Variables shared between different process
tnote = Value('q', 0)  # note's PC timming
knote = Value('q', 0)  # note's key (for joystick midi feedback play)
tnotes_log = Array('l', [0] * JOY_BUFF_SIZE)  # Save notes timming fo the log 
# This loop only plays the MIDI file. Only gives back the note time and event ocurrance flag
# THIS RUNS IN A SEPARATE PROCESS, SO ONLY THE PARAMETERS CAN BE SHARED TO THE REST OF THE PROGRAM
def playMidi( portname, filename, tnote, knote, tnotes_log, start_event):
    output = mido.open_output(portname)
    midifile = MidiFile(filename)

    # sleep until the video starts playing
    start_event.wait()
    print ("midi started")

    event_counter = 0
    for msg in midifile.play():  # This function gets stuck here, until a new midi note ocurrs in mido
        if MIDI_PLAY_MIDIFILE_NOTES == True:
            output.send(msg)

        if msg.type == 'note_on' and msg.velocity > 0:
            now = int(time.time_ns() / 1000000)
            tnote.value = now
            knote.value = msg.note
            
            #save note data into the log 
            tnotes_log[event_counter] = now
            event_counter = event_counter + 1

    output.reset()
    return

# Variables shared between different process
hit = Value('b', False)  # registers if the last not was a good hit or not (for visual feedback)
event = Value('b', False )    # if a note on event has happened flag
hit_notes_log = Array('l', [0] * JOY_BUFF_SIZE)   # Saves the time of the good hit joystick events (all the other are misses)  
hit_joy_log = Array('l', [0] * JOY_BUFF_SIZE)   # Saves the time of the good hit note events (all the other are misses)  
# Checks for user input, registers good and bad hits and save the logged data into disk (on finish)
# THIS RUNS IN A SEPARATE PROCESS, SO ONLY THE PARAMETERS CAN BE SHARED TO THE REST OF THE PROGRAM
def userInput(portname, joyTimeBuf, jBufIndx, hit, tnote, knote, event, hit_notes_log, hit_joy_log):
    output = mido.open_output(portname)

    pc = mido.Message('program_change', channel=8, program=116, time=0 )   # setup of taiko sound
    output.send(pc)

    prev_note_time = 0
    hits_counter = 0
    while(True):
        now = int(time.time_ns() / 1000000)
        note_time = tnote.value

        if  now >= (note_time + MIDI_MAX_FUTURE) and prev_note_time != note_time:                 

            # Check the buffered joystick entries are miss or hit
            nhits = 0   # counts the number of hits   
            jindx = jBufIndx.value
            jtime = 0
            while ( ( abs(note_time - joyTimeBuf[jindx]) <= MIDI_MAX_PAST )  ):

                # print (jindx, MIDI_MAX_PAST, note_time - joyTimeBuf[jindx], abs(note_time - joyTimeBuf[jindx]) >= MIDI_MAX_PAST  )  # DEBUG
                nhits = nhits + 1
                jtime = joyTimeBuf[jindx]

                jindx = jindx - 1
                if jindx < 0:
                    jindx = JOY_BUFF_SIZE -1

            # IF ZERO HITS OR MORE THAN 1 HIT OCCUR THEN IT IS A MISS
            if nhits == 1:  # HIT 
                hit.value = True   # good hit flag             

                # play MIDI note 
                if MIDI_PLAY_GOOD_HITS:
                    pnote = mido.Message('note_on', channel=8, note=knote.value, velocity=127, time=0)
                    output.send(pnote)

                # log hit event 
                hit_notes_log[hits_counter] = note_time
                hit_joy_log[hits_counter] = jtime
                hits_counter = hits_counter + 1

                print ("HIT")
            else:          # MISS
                hit.value = False   # miss hit flag
                print ("MISS")

            prev_note_time = note_time  
            event.value = True
    return 

    

# Controls the MIDI music play and also calculates the timming with the given 
# joystick timmming (joyTime)
class MidiControl:

    # portname - Midi portname
    # filename - Midi filename to play
    # joyTime - multiprocessing Value object to track Joystick time events
    def __init__(self, portname, filename, logfile, joyTimeBuf, jBufIndx, start_event, joy_log):    

        print (mido.get_output_names())   # prints midi available midi outputs
        self.log_file = logfile
        self.joy_log = joy_log
        
        self.p_midi = Process(name="p_midi", target=playMidi, args=(portname, filename, tnote, knote, tnotes_log, start_event  ))
        # self.p_midi = Process(name="p_midi", target=playMidi, args=(portname, filename,  ))
        self.p_input = Process(name="p_input", target=userInput, args=(portname, joyTimeBuf, jBufIndx, hit, tnote, knote, event, hit_notes_log, hit_joy_log ))
        
    # Starts the muliprocess
    def start(self):
        self.p_midi.start()
        self.p_input.start()
        print ("midi empezo")

    # Kills the process
    def stop(self):
        if self.p_midi.is_alive():  
            self.p_midi.terminate()
            self.p_midi.join()

        if self.p_input.is_alive():
            self.p_input.terminate()
            self.p_input.join()

        # Join input, joystick and midi events logs into one single file
        # self.logOnDisk()

    def isNewEvent(self):
        return [event.value, hit.value]

    def eventFinished(self):
        event.value = False

    # Save all the timming note/joystick events logs on disk  (MIDI note, GOOD hits and joystick events)
    # def logOnDisk(self):
    #     full_log = []
    #     for jtime, jindx in enumerate(joy_log):
    #         jhit = -1

    #         for j_hit_time, j_hit_index in enumerate(hit_joy_log):
    #             if jtime == j_hit_time:
    #                 jhit = jindx
    #                 break

    #         if jhit == -1:  # MISS
    #             full_log.append([jtime, 0, 0, 0])

    #         else: # HIT


    #     with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:

    #         wr.writerow(['Joystick_Press(ms)', 'Note_Time(epoch)', 'Reaction_Time(nearest_note)', 'Hit_or_Miss', ])

            

            
                
                      


            

            




              


            


        # with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
        #     wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #     wr.writerow(['Hit_or_Miss', 'Joystick_Press(ms)', 'Note_Time(epoch)', 'GOOD_Hit_Time(epoch)', 'Reaction_Time'])


        #     first_event = 0
        #     last_hit = 0  # for discard un-pressed events otherwise the same hit timming will be logged

        #     for i, event in enumerate(event_log):
        #         timming = event[1] - event[2]
        #         if (i ==0):
        #             first_event = event[1]
        #         if (last_hit - event[2] == 0):
        #             wr.writerow(  ( '0', event[1]-first_event, event[1], '0', '0', event[4] ) )
        #         else:
        #             wr.writerow(  ( '0', event[1]-first_event, event[1], event[2], timming, event[4] ) )
        #         last_hit = event[2]


    # Save all the timming note/joystick events logs on disk 
    # def logOnDisk(self, event_log):
    #     with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
    #         wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
    #         wr.writerow(['User_ID', 'Time_Lapse(ms)', 'Time(epoch)', 'Hit_Time(epoch)', 'Timming', 'Hit'])
    #         first_event = 0
    #         last_hit = 0  # for discard un-pressed events otherwise the same hit timming will be logged
    #         for i, event in enumerate(event_log):
    #             timming = event[1] - event[2]
    #             if (i ==0):
    #                 first_event = event[1]
    #             if (last_hit - event[2] == 0):
    #                 wr.writerow(  ( '0', event[1]-first_event, event[1], '0', '0', event[4] ) )
    #             else:
    #                 wr.writerow(  ( '0', event[1]-first_event, event[1], event[2], timming, event[4] ) )
    #             last_hit = event[2]


    # def isNewEvent(self):
    #     # NOTE: This function may have race conditions problems... 
    #     #       it needs further testing 
    #     lastEvents = []
    #     if event.value == True:
    #         event.value = False
    #         if (self.tnote.value - hits[0]) < MIDI_MAX_PAST:
    #             # print("short OK : " + str(hits[i]))
    #             self.event_log.append((0, self.tnote.value, hits.value, 0, 1))
    #             lastEvents.append(self.event_log[-1])

    #         elif (self.tnote.value - hits[0]) < MIDI_MAX_FUTURE:
    #             # print("long  OK : " + str(hits[i]))
    #             self.event_log.append((0, self.tnote.value, hits.value, 0, -1))
    #             lastEvents.append(self.event_log[-1])
    #         else:
    #             # print("FAIL: " + str(hits[i]))
    #             self.event_log.append((0, self.tnote.value, hits.value, 0, -1))
    #             lastEvents.append(self.event_log[-1])
    #     return lastEvents


    

    
                