
import pygame
import time
from threading import Thread

class Joystick:
    def __init__(self):
        # Pygame init and Joystick init 
        pygame.init()
        pygame.joystick.init()
        self.jCount = pygame.joystick.get_count()
        self.joystick = []
        if self.jCount > 0:
            for i in range(0, self.jCount):
                self.joystick.append(pygame.joystick.Joystick(i))
                self.joystick[-1].init()

        # Init class variables
        self.joyPressed = [self.jCount] * False
        self.run = False

    # starts the thread 
    def start(self, joyTime):

        # Init Threading
        # joyTime.value = 0    # saves the time when the taiko was pressed
        self.joyThread = Thread(target=self.joystickLoop, args=(joyTime,))
        self.joyThread.daemon = True

        self.run = True
        self.joyThread.start() 
    
    # stops the thread main cycle
    def stop(self):
        self.run = False

    # returns the status of all the press events of all the joysticks
    def getJoysticksEvents(self):
        r = []
        if self.joystick is not None:
            for index in range(0,self.jCount):
                l_taiko = self.joystick[index].get_button(8)
                r_taiko = self.joystick[index].get_button(9)
                r.append( (l_taiko, r_taiko) )
        return r

    def isPressed(self):
        return self.joyPressed

    def joystickLoop(self, joyTime):
        self.joyPressed = [False] * self.jCount
        while self.run:
            for event in pygame.event.get(): # User did something.
                if event.type == pygame.JOYBUTTONDOWN:
                    taiko = self.getJoysticksEvents()
                    for index in range(0, self.jCount):
                        if (taiko[index][0] == 1 or taiko[index][1] == 1) and self.joyPressed[index] == False and taiko is not None:
                            joyTime[index] = int(time.time() * 1000)
                            self.joyPressed[index] = True
                            # print (index)
                            # print("Joystick button pressed.")   # DEBUG
                elif event.type == pygame.JOYBUTTONUP:
                    taiko = self.getJoysticksEvents()
                    for index in range(0, self.jCount):
                        if taiko[index][0] == 0 or taiko[index][1] == 0:
                            if self.joyPressed[index]:
                                self.joyPressed[index] = False
                                # print (index)
                                # print("Joystick button released.")   # DEBUG