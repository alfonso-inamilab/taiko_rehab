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
    def __init__(self, portname, filename, joyTime):
        TIME_LENGHT =  1000 #in (ms)  
        self.MAX_PAST = TIME_LENGHT // 2
        self.MAX_FUTURE = TIME_LENGHT // 4
        self.p = Process(target=self.playMidi, args=(portname, filename, joyTime))
        self.p.daemon = True

    # Starts the muliprocess
    def start(self):
        self.p.start()

    # Kills the process
    def stop(self):
        if self.p.is_alive():  
            self.p.terminate()
            self.p.join()

    # Main process loop. Plays the MIDI and checks for Joystick time events to calculate the timming. 
    def playMidi(self, portname, filename, joyTime):
        output = mido.open_output(portname)
        midifile = MidiFile(filename)

        for message in midifile.play():
            if message.type == 'note_on' and message.velocity > 0:
                now = int(time.time() * 1000)
                hit =  now - joyTime.value
                if hit < self.MAX_PAST:
                    print("short OK : " + str(hit))
                elif hit < self.MAX_FUTURE:
                    print("long  OK : " + str(hit))
                else:
                    print("FAIL: " + str(hit))

                print(message)
            output.send(message)
        output.reset()
        return
