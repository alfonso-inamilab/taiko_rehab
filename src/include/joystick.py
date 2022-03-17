
import pygame
import time
import mido
import csv
from threading import Thread

from include.globals import JOY_BUFF_SIZE
from include.globals import MIDI_PLAY_ALL_HITS

class Joystick:
    def __init__(self):
        # Pygame init and Joystick init 
        pygame.init()
        pygame.joystick.init()
        self.jCount = pygame.joystick.get_count()
        self.joystick = pygame.joystick.Joystick(0)

        # Init class variables
        self.joyPressed = False
        self.run = False

    # starts the thread 
    def start(self, midi_port, joyTimeBuf, jBufIndx, joy_log):

        # Init Threading
        self.joyThread = Thread(target=self.joystickLoop, args=(midi_port, joyTimeBuf,jBufIndx, joy_log))
        self.joyThread.daemon = True

        self.run = True
        self.joyThread.start() 
    
    # stops the thread main cycle
    def stop(self):
        self.run = False

    # returns the status of all the press events of all the joysticks
    def getJoysticksEvents(self):
        r = (0, 0)
        if self.joystick is not None:            
            l_taiko = self.joystick.get_button(8)
            r_taiko = self.joystick.get_button(9)
            r = (l_taiko, r_taiko) 
        return r

    def isPressed(self):
        return self.joyPressed

    def joystickCheck(self):
        if self.jCount <=0:
            return False
        else:
            return True

    def joystickLoop(self, midi_port, joyTimeBuf, jBufIndx, joy_log):
        output = mido.open_output(midi_port)
 
        pc = mido.Message('program_change', channel=8, program=116, time=0 )   # setup of taiko sound
        output.send(pc)

        self.joyPressed = False
        jBufIndx.value = 0
        event_counter = 0
        while self.run:
            for event in pygame.event.get(): # User did something.
                if event.type == pygame.JOYBUTTONDOWN:
                    taiko = self.getJoysticksEvents()

                    if (taiko[0] == 1 or taiko[1] == 1) and self.joyPressed == False and taiko is not None:
                        jBufIndx.value = jBufIndx.value + 1
                        if jBufIndx.value >= JOY_BUFF_SIZE:
                            jBufIndx.value = 0
                        now = int(time.time_ns() / 1000000)
                        joyTimeBuf[jBufIndx.value] = now
                        
                        joy_log[event_counter] = now
                        event_counter = event_counter + 1
                        self.joyPressed = True

                        if MIDI_PLAY_ALL_HITS:
                            pnote = mido.Message('note_on', channel=8, note=64, velocity=127, time=0)
                            output.send(pnote)

                        # print ("press", joyTime)
                        # print("Joystick button pressed.")   # DEBUG
                elif event.type == pygame.JOYBUTTONUP:
                    taiko = self.getJoysticksEvents()

                    
                    if taiko[0] == 0 or taiko[1] == 0:
                        if self.joyPressed:
                            self.joyPressed = False
                            # print("Joystick button released.")   # DEBUG

        print ("joystick thread stop...")
        return 
        