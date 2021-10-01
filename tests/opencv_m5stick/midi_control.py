import sys
import time
import mido
from mido import MidiFile 
from multiprocessing import Process, Value, Array

# Controls the MIDI music play and also calculates the timming with the given 
# joystick timmming (joyTime)
class MidiControl:

    # portname - Midi portname
    # filename - Midi filename to play
    # joyTime - multiprocessing Value object to track Joystick time events
    def __init__(self, portname, channel, filename, joyTime, joyForces, numJoysticks):
        TIME_LENGHT =  1000 #in (ms)  
        self.MAX_PAST = TIME_LENGHT // 4
        self.MAX_FUTURE = TIME_LENGHT // 8
        
        self.jCount = numJoysticks
        self.joyForces = joyForces
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
        if self.event.value == True:
            self.event.value = False

            lastEvents = []
            for i in range (0,self.jCount):

                if self.hits[i] < self.MAX_PAST:
                    # print("short OK : " + str(self.hits[i]))
                    self.event_log.append((i, self.tnote.value, self.hits[i], self.joyForces[i], True))
                elif self.hits[i] < self.MAX_FUTURE:
                    # print("long  OK : " + str(self.hits[i]))
                    self.event_log.append((i, self.tnote.value, self.hits[i], self.joyForces[i], True))
                else:
                    # print("FAIL: " + str(self.hits[i]))
                    self.event_log.append((i, self.tnote.value, self.hits[i], self.joyForces[i], False))
            
                lastEvents.append(self.event_log[-1])
            # print (self.event_log)
            return lastEvents
        return None
            

    # Main process loop. Plays the MIDI and checks for Joystick time events to calculate the timming. 
    def playMidi(self, portname, filename, joyTime, tnote, hits, event):
        output = mido.open_output(portname)
        midifile = MidiFile(filename)

        pc = mido.Message('program_change', channel=8, program=116, time=0 )
        output.send(pc)

        for msg in midifile.play():
            if msg.type == 'note_on' and msg.velocity > 0:
                # now = int(time.time() * 1000)
                # hit =  now - joyTime.value
                now = int(time.time() * 1000)
                tnote.value = now
                for i in range(0, self.jCount):
                    hits[i] = now - joyTime[i]

                    print(hits[i])
                    if hits[i] < self.MAX_FUTURE or hits[i] < self.MAX_PAST:
                        pnote = mido.Message('note_on', channel=8, note=msg.note, velocity=127, time=0)
                        output.send(pnote)
                
                event.value = True
                # print(msg)

            output.send(msg)
        output.reset()
        return
