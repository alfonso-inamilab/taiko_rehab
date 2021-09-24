import sys
import time
import mido
from mido import MidiFile 
from multiprocessing import Process, Value

# Controls the MIDI music play and also calculates the timming with the given 
# joystick timmming (joyTime)
class MidiControl:

    # portname - Midi portname
    # filename - Midi filename to play
    # joyTime - multiprocessing Value object to track Joystick time events
    def __init__(self, portname, channel, filename, joyTime):
        TIME_LENGHT =  1000 #in (ms)  
        self.MAX_PAST = TIME_LENGHT // 2
        self.MAX_FUTURE = TIME_LENGHT // 4
        
        self.tnote = Value('q', 0)  # note's PC timming
        self.hit = Value('q', 0)   
        self.event = Value('b', False)  

        self.p = Process(target=self.playMidi, args=(portname, filename, joyTime, self.tnote, self.hit, self.event))
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

            if self.hit.value < self.MAX_PAST:
                # print("short OK : " + str(self.hit))
                self.event_log.append((self.tnote.value, self.hit.value, True))
            elif self.hit.value < self.MAX_FUTURE:
                # print("long  OK : " + str(self.hit))
                self.event_log.append((self.tnote.value, self.hit.value, True))
            else:
                # print("FAIL: " + str(self.hit))
                self.event_log.append((self.tnote.value, self.hit.value, False))
            # print (self.event_log)
            return self.event_log[-1]
        return None
            

    # Main process loop. Plays the MIDI and checks for Joystick time events to calculate the timming. 
    def playMidi(self, portname, filename, joyTime, tnote, hit, event):
        output = mido.open_output(portname)
        midifile = MidiFile(filename)

        for msg in midifile.play():
            if msg.type == 'note_on' and msg.velocity > 0:
                # now = int(time.time() * 1000)
                # hit =  now - joyTime.value
                now = int(time.time() * 1000)
                tnote.value = now
                hit.value = now - joyTime.value
                event.value = True
                # print(msg)
            output.send(msg)
        output.reset()
        return
