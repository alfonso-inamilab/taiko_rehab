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
tnotes_log = Array('q', [0] * JOY_BUFF_SIZE)  # Save notes timming fo the log 
# This loop only plays the MIDI file. RUNS USING THE FPS FROM THE VIDEO FOR GOOD SYNC
def playMidi( portname, filename, tnote, knote, tnotes_log, start_event, vt):
    output = mido.open_output(portname)
    event_counter = 0

    start_time = vt.value
    input_time = 0
    first_note = False

    for msg in MidiFile(filename):
        input_time = int(msg.time*1000)

        playback_time = vt.value - start_time
        duration_to_next_event = input_time - playback_time

        if duration_to_next_event > 0:
            time.sleep(duration_to_next_event/1000.0)

        if msg.is_meta:
            continue
        else:
            if (msg.type == 'note_on') and not first_note:
                start_event.wait()
                start_time = vt.value
                first_note = True

            if MIDI_PLAY_MIDIFILE_NOTES == True:
                output.send(msg)
            
            if msg.type == 'note_on' and msg.velocity > 0:
                now = int(time.time_ns() / 1000000) 
                tnote.value = now
                knote.value = msg.note
            
                #save note data into the log 
                tnotes_log[event_counter] = now
                event_counter = event_counter + 1


        if msg.is_meta:
            continue
        else:
            if msg.type == 'note_on' and msg.velocity > 0:
                if first_note == True:
                    start_event.wait()
                    first_note = False
                
    output.reset()
    print ("MIDI thread stop...")
    return

# Variables shared between different process
hit = Value('b', False)  # registers if the last not was a good hit or not (for visual feedback)
event = Value('b', False )    # if a note on event has happened flag
hit_notes_log = Array('q', [0] * JOY_BUFF_SIZE)   # Saves the time of the good hit joystick events (all the other are misses)  
hit_joy_log = Array('q', [0] * JOY_BUFF_SIZE)   # Saves the time of the good hit note events (all the other are misses)  
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
    
    print ("User Input thread stop...")
    return 

    

# Controls the MIDI music play and also calculates the timming with the given 
# joystick timmming (joyTime)
class MidiControl:

    # portname - Midi portname
    # filename - Midi filename to play
    # joyTime - multiprocessing Value object to track Joystick time events
    def __init__(self, portname, log_path, filename, joyTimeBuf, jBufIndx, start_event, joy_log, timestamp):    

        print (mido.get_output_names())   # prints midi available midi outputs
        self.log_path = log_path
        self.log_file = log_path + os.path.sep + 'midi_log.csv'
        self.joy_log = joy_log
        
        self.p_midi = Process(name="p_midi", target=playMidi, args=(portname, filename, tnote, knote, tnotes_log, start_event, timestamp  ))
        self.p_input = Process(name="p_input", target=userInput, args=(portname, joyTimeBuf, jBufIndx, hit, tnote, knote, event, hit_notes_log, hit_joy_log ))
        self.p_midi.daemon = True   
        self.p_input.daemon = True
        
    # Starts the muliprocess
    def start(self):
        self.p_midi.start()
        self.p_input.start()

    # Kills the process
    def stop(self):
        if self.p_midi.is_alive():  
            self.p_midi.terminate()
            self.p_midi.join()

        if self.p_input.is_alive():
            self.p_input.terminate()
            self.p_input.join()

        # Join input, joystick and midi events logs into one single file
        self.logOnDisk()

    def isNewEvent(self):
        return [event.value, hit.value]

    def eventFinished(self):
        event.value = False

    # Save all the timming note/joystick events logs on disk  (MIDI note, GOOD hits and joystick events)
    def logOnDisk(self):
        # Join the joystick hits info with the note OK hits information
        joyhits = []
        for joy_indx, joy_time in enumerate(self.joy_log):

            row = [joy_time, 0, 0, 0]
            for  hit_indx, hit_time in enumerate (hit_joy_log):

                if joy_time == hit_time:
                    row = [joy_time, hit_notes_log[hit_indx], (hit_notes_log[hit_indx] - joy_time) , 1 ]
                    break
            
            if row[0] != 0:   # do add empty joystick buffer slots
                joyhits.append(row)
                    
        # Add the MISSED notes to the joined table 
        # copy_joyhits = joyhits.copy()
        for n_index, n_time in enumerate(tnotes_log):

            insert_index = -1
            for index, row in enumerate(joyhits):
                if row[1] == n_time:
                    break
                elif row[1] > n_time:
                    insert_index = index
                    break
            # if note is note found (MISS), insterted  on the insert index
            if insert_index != -1:
                miss_note_row = [ 0, n_time, 0 , 0]   
                joyhits.insert(insert_index, miss_note_row)         

        with open( self.log_path + os.path.sep + 'midi_hits_log.csv', 'w', newline='', encoding='utf-8') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            wr.writerow(['Index', 'Joystick Hit Time(epoch-ms)'," Note Time(epoch-ms)", "Time Difference(ms)", 'Hit(bool)'])

            for indx, row in enumerate(joyhits):
                wr.writerow([indx,row[0],row[1],row[2],row[3]])
