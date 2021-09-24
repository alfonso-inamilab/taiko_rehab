
import pygame
import time
from threading import Thread

class Joystick:
    def __init__(self, joyTime):
        # Pygame init and Joystick init 
        pygame.init()
        pygame.joystick.init()
        joystick_count = pygame.joystick.get_count()
        self.joystick = None
        if joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

        # Init Threading
        self.run = False
        joyTime.value = 0    # saves the time when the taiko was pressed
        self.joyThread = Thread(target=self.joystickLoop, args=(joyTime,))
        self.joyThread.daemon = True

        # Init class variables
        self.joyPressed = False 
        
    # starts the thread 
    def start(self):
        self.run = True
        self.joyThread.start() 
    
    # stops the thread main cycle
    def stop(self):
        self.run = False

    def getJoystickEvent(self, index):
        if self.joystick is not None:
            l_taiko = self.joystick.get_button(8)
            r_taiko = self.joystick.get_button(9)
            return [l_taiko, r_taiko]
        return [0,0]

    def isPressed(self):
        return self.joyPressed

    def joystickLoop(self, joyTime):
        self.joyPressed = False
        while self.run:
            for event in pygame.event.get(): # User did something.
                if event.type == pygame.JOYBUTTONDOWN:
                    taiko = self.getJoystickEvent(0)
                    if (taiko[0] == 1 or taiko[1] == 1) and self.joyPressed == False:
                        joyTime.value = int(time.time() * 1000)
                        self.joyPressed = True
                        # print("Joystick button pressed.")   # DEBUG
                elif event.type == pygame.JOYBUTTONUP:
                    taiko = self.getJoystickEvent(0)
                    if taiko[0] == 0 or taiko[1] == 0:
                        if self.joyPressed:
                            self.joyPressed = False
                            # print("Joystick button released.")   # DEBUG