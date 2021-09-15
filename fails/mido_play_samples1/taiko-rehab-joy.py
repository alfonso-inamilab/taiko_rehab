# general imports 
import sys
import mido
import pygame
import time

from mido import MidiFile 
from multiprocessing import Process, Value

# GLOBAL VARIABLES 
TIME_LENGHT =  1000 #in (ms)  
MAX_PAST = TIME_LENGHT // 2
MAX_FUTURE = TIME_LENGHT // 4
JOY_CHANNEL = 0

# PYGAME AND JOYSTICK INIT
global joystick
pygame.init()
pygame.joystick.init()
joystick_count = pygame.joystick.get_count()
joystick = None
if joystick_count > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

def getJoystickEvent(index):
    global joystick
    if joystick is not None:
        l_taiko = joystick.get_button(8)
        r_taiko = joystick.get_button(9)
        return [l_taiko, r_taiko]
    return [0,0]

def joystickLoop(joyTime):
    joyPress = False
    while True:
        for event in pygame.event.get(): # User did something.
            if event.type == pygame.JOYBUTTONDOWN:
                taiko = getJoystickEvent(0)
                if (taiko[0] == 1 or taiko[1] == 1) and joyPress == False:
                    joyTime.value = int(time.time() * 1000)
                    joyPress = True
                    # print("Joystick button pressed.")
            elif event.type == pygame.JOYBUTTONUP:
                taiko = getJoystickEvent(0)
                if taiko[0] == 0 or taiko[1] == 0:
                    if joyPress:
                        joyPress = False
                        # print("Joystick button released.")
                

def playMidi(portname, filename, joyTime):
    output = mido.open_output(portname)
    midifile = MidiFile(filename)

    try:
        for message in midifile.play():
            if message.type == 'note_on' and message.velocity > 0:
                now = int(time.time() * 1000)
                hit =  now - joyTime.value
                if hit < MAX_PAST:
                    print("short OK : " + str(hit))
                elif hit < MAX_FUTURE:
                    print("long  OK : " + str(hit))
                else:
                    print("FAIL: " + str(hit))

                print(message)
            output.send(message)
        output.reset()
        return
    except KeyboardInterrupt:
        output.reset()
        print("MIDI process closed.")
        return

def main():
    filename = sys.argv[1]
    if len(sys.argv) == 3:
        portname = sys.argv[2]
    else:
        portname = None

    joyTime = Value('q', 0)  #type must be double long
    p = Process(target=playMidi, args=(portname, filename, joyTime))
    p.start()
    
    j = Process(target=joystickLoop, args=(joyTime, ))
    j.start()

    
    p.join()
    j.join()
    
if __name__ == "__main__":
    main()

