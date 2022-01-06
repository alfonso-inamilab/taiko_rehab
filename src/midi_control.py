import sys
import mido
import os
import csv
import time
import datetime
from mido import MidiFile 
from multiprocessing import Process, Value, Array

# Controls the MIDI music play and also calculates the timming with the given 
# joystick timmming (joyTime)
class MidiControl:

    # portname - Midi portname
    # filename - Midi filename to play
    # joyTime - multiprocessing Value object to track Joystick time events
    def __init__(self, portname, channel, filename, joyTime, joyForces, numJoysticks ):
        TIME_LENGHT =  1000 #in (ms)  
        self.MAX_PAST = TIME_LENGHT // 2
        self.MAX_FUTURE = TIME_LENGHT // 8
        
        self.jCount = numJoysticks
        self.joyForces = joyForces
        self.log_file = os.path.splitext(filename)[0] + "_log.csv"
        self.tnote = Value('q', 0)  # note's PC timming
        self.hits = Array('q', [0] * self.jCount)    # hit timming for each user
        self.event = Value('b', False )    # if a note on event has happened flag

        self.p = Process(target=self.playMidi, args=(portname, filename, joyTime, self.tnote, self.hits, self.event))
        self.ch = channel
        
        self.event_log = []

    # Starts the muliprocess
    def start(self):
        self.p.start()

    # Kills the process
    def stop(self):
        if self.p.is_alive():  
            self.p.terminate()
            self.p.join()

    def isNewEvent(self):
        # NOTE: This function may have race conditions problems... 
        #       it needs further testing 
        lastEvents = []
        if self.event.value == True:
            self.event.value = False

            for i in range (0,self.jCount):
                if (self.tnote.value - self.hits[i]) < self.MAX_PAST:
                    # print("short OK : " + str(self.hits[i]))
                    self.event_log.append((i, self.tnote.value, self.hits[i], self.joyForces[i], 1))
                    lastEvents.append(self.event_log[-1])

                elif (self.tnote.value - self.hits[i]) < self.MAX_FUTURE:
                    # print("long  OK : " + str(self.hits[i]))
                    self.event_log.append((i, self.tnote.value, self.hits[i], self.joyForces[i], -1))
                    lastEvents.append(self.event_log[-1])
                else:
                    # print("FAIL: " + str(self.hits[i]))
                    self.event_log.append((i, self.tnote.value, self.hits[i], self.joyForces[i], -1))
                    lastEvents.append(self.event_log[-1])

        return lastEvents

    # Save all the timming note/joystick events logs on disk 
    def logOnDisk(self):
        with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            
            wr.writerow(['User_ID', 'Time_Lapse(ms)', 'Time(epoch)', 'Hit_Time(epoch)', 'Timming', 'Hit'])
            first_event = 0
            last_hit = 0  # for discard un-pressed events otherwise the same hit timming will be logged
            for i, event in enumerate(self.event_log):
                timming = event[1] - event[2]
                if (i ==0):
                    first_event = event[1]
                if (last_hit - event[2] == 0):
                    wr.writerow(  ( '0', event[1]-first_event, event[1], '0', '0', event[4] ) )
                else:
                    wr.writerow(  ( '0', event[1]-first_event, event[1], event[2], timming, event[4] ) )
                last_hit = event[2]
                

    # Main process loop. Plays the MIDI and checks for Joystick time events to calculate the timming. 
    # REMEMBER: This is an independet process, so the variables are NOT shared with the main thread. 
    def playMidi(self, portname, filename, joyTime, tnote, hits, event):
        output = mido.open_output(portname)
        midifile = MidiFile(filename)

        pc = mido.Message('program_change', channel=8, program=116, time=0 )
        output.send(pc)


        for msg in midifile.play():
            if msg.type == 'note_on' and msg.velocity > 0:
                now = int(time.time() * 1000)
                tnote.value = now
                for i in range(0, self.jCount):
                    hits[i] = joyTime[i]
                    joyhit = now - hits[i]
                    if joyhit < self.MAX_FUTURE or joyhit < self.MAX_PAST:
                        pnote = mido.Message('note_on', channel=8, note=msg.note, velocity=127, time=0)
                        output.send(pnote)
                
                event.value = True
            output.send(msg)
        output.reset()

        return
