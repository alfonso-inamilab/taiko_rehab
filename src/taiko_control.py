# Example to use a webcam with OpenCV Demo for python. 
# TODO Get (aproximate) the arms velocity
# TODO Implement taiko joystick wcontrols
# TODO MIDI audio synthesizer 
import sys
import cv2
import os
import time
import math
from sys import platform
import argparse
import pygame
import ctypes
import numpy as np
from multiprocessing import Array, Value

# IMPORTING GLOBAL PARAMETERS 
from include.globals import OP_PY_DEMO_PATH
from include.globals import OP_MODELS_PATH
from include.globals import CAM_OPCV_ID
from include.globals import MAX_TXT_FRAMES
from include.globals import FULL_LOG_FILE
from include.globals import ARMS_LOG_NAME
from include.globals import FORCE_LOG_NAME
from include.globals import MIDI_LOG_NAME
from include.globals import DRAW_SENSEI_ARMS

# TAIKO REHAB MODULES
from include.cameraThread import camThread
# PYGAME JOYSTICK TO CATCH TIME EVENTS
from include.joystick import Joystick
# MIDO TO PLAY MIDI AND MEASURE TIMMING
from include.midi_control import MidiControl
# CLASS TO CALCULATE AND LOG ARMS AND SHOULDERS POSITION
from include.arm_angle_logger import ArmAngleLog
# CLASS TO READ THE FORCE/ACC FROM THE SENSOR
from include.m5stick_serial_acc import M5SerialCom
# CLASS TO DISPLAY SIMULTANEOUS VIDEO DISPLAY 
from include.video_display import VideoDisplay

#This class controls the main program exceuction 
class taikoControl():
    
    # Inits all the variables of the main program
    def init (self):
        # thread objects
        self.opWrapper = None
        self.cam = None
        self.video = None
        self.joy = None
        self.m4 = None #m5 communication control thread
        self.midi = None #thread for midi control
        self.armsPos  = None # logs/calc/compare the users arms position

        # variables for thread control
        self.datum = None
        self.timestamp = None # video timestamp
        self.joyTime = None  # joystick pressing time
        self.joyForces = None # saves the joystick hit force
        self.txtFrames = None # Number of cycles hit feedback appears on the screen
        self.hit_vel = None   # To print the velocity on the screen
        self.hit_ok = None  # To print the hit miss or fail on the screen
        self.first = None # To detect the first process cycle
        

    def initThreads(self,  csv_path, video_path, midi_path):
        # try:
            # Init camera thread
            # cap = cv2.VideoCapture(CAM_OPCV_ID, cv2.CAP_DSHOW)
            self.cam = camThread(CAM_OPCV_ID, 200)  # Init camera thread object
            self.cam.start()   # Start camera capture

            self.timestamp = Value('i', 0)
            self.video = VideoDisplay( video_path, self.timestamp, 200, video_scale=0.5)  # video display 

            # Init Joystick       
            self.joy = Joystick()
            self.joyTime = Array('q', [0] * self.joy.jCount)  # Sync object to save the joystick number and timming
            self.joy.start(self.joyTime)   # Init thread and start joystick event catch thread

            # Init M5 acc serial thread
            self.joyForces = Array('f', [0] * self.joy.jCount)  # object to save the joysitck hit force
            
            # FOR MULTIPLE USER (DEPRECATED)
            # self.m5 = []
            # ex = os.path.splitext(FORCE_LOG_NAME)
            # for i in range(0,self.joy.jCount):
            #     self.m5.append( M5SerialCom( bauds=115200, port='COM5', joyForces=self.joyForces, joyIndex = i, log_file=ex[0]+str(i)+'.csv' )
            #     self.m5[-1].start()
            # FOR A SINGLE USER
            self.m5 = M5SerialCom( bauds=115200, port='COM5', joyForces=self.joyForces, joyIndex = 0, log_file=FORCE_LOG_NAME )
            self.m5.start()

            # Init MIDI control process
            self.midi = MidiControl(portname=None, channel=0, filename=midi_path, logfile=MIDI_LOG_NAME, joyTime=self.joyTime, joyForces=self.joyForces, numJoysticks=self.joy.jCount)

            # Logs the users' arms positions
            self.armsPos = ArmAngleLog(self.cam.resX, self.cam.resY, csv_path, log_file=ARMS_LOG_NAME)

            self.txtFrames = MAX_TXT_FRAMES  # Number of cycles hit feedback appears on the screen
            self.hit_vel = 0   # To print the velocity on the screen
            self.hit_ok = False  # To print the hit miss or fail on the screen
            self.first = True # To detect the first process cycle

        # except Exception as e:
        #     print(e)
        #     sys.exit(-1)

    def videoPreProcess(self, video_path, save_csv_path):
        self.video = VideoDisplay( "", None, 0)
        self.video.video_pre_proc(video_path, save_csv_path)


    def startTraining(self):
        try:
            # Import Openpose (Windows)
            try:       
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append(OP_PY_DEMO_PATH + '/../../python/openpose/Release');
                os.environ['PATH']  = os.environ['PATH'] + ';' + OP_PY_DEMO_PATH + '/../../x64/Release;' +  OP_PY_DEMO_PATH + '/../../bin;'
                import pyopenpose as op
            except ImportError as e:
                print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
                raise e

            # Flags
            parser = argparse.ArgumentParser()
            # parser.add_argument("--image_path", default="../../../examples/media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
            args = parser.parse_known_args()

            # Custom Params (refer to include/openpose/flags.hpp for more parameters)
            # Add other parameters for OpenPose here
            params = dict()
            params["model_folder"] = OP_MODELS_PATH
            params["number_people_max"] = 1 #MAX_NUM_PEOPLE
    
            # Init OpenPose python wrapper
            self.opWrapper = op.WrapperPython()
            self.opWrapper.configure(params)
            self.opWrapper.start()
            self.datum = op.Datum()


            # start = 0
            # img = None 
            # events = None
            # arms_matches = None
            # end = 0
            while True:
                start = time.time()
                img = self.cam.get_video_frame()  #rgb right camera
                if img is None:
                    continue

                self.datum.cvInputData = img
                self.opWrapper.emplaceAndPop(op.VectorDatum([self.datum]))

                # Estimate the position and velocity of the arms and shoulders
                if self.datum.poseKeypoints is not None:
                    events = self.midi.isNewEvent()
                    # Draws the person ID over his head
                    # img = self.armsPos.drawPersonNum(img, self.datum.poseKeypoints)
                    if DRAW_SENSEI_ARMS:
                        img = self.armsPos.drawSenseiArms(img, self.datum.poseKeypoints)
                    # calcs the arm and shoulder angular velocity
                    self.armsPos.calcArmVel(self.datum.poseKeypoints)
                    # Checks if the users arms and instructors arms (video) match
                    arms_matches = self.armsPos.getArmsMatch(self.timestamp, 0.8) # must be called after calcArmVel
                    # Draws the skeleton of the user's arms (changes accordingly to match)
                    self.armsPos.drawSkeleton(img, self.datum.poseKeypoints, arms_matches, 0.8)
                    if events:  
                        self.txtFrames = 0

                        if self.txtFrames < MAX_TXT_FRAMES:
                            img = self.armsPos.drawHit(img, events, self.datum.poseKeypoints)    # Draws if hit were OK or NOT
                            self.txtFrames = self.txtFrames + 1

                end = time.time()
                # print("Frame total time: " + str(end - start) + " seconds")  # DEBUG
            
                # img = cv2.resize(img, ((int)(img.shape[1]*0.5), (int)(img.shape[0]*0.5)) , interpolation = cv2.INTER_AREA  )
                # if first:
                #     cv2.namedWindow("Taiko Rehab", cv2.WINDOW_NORMAL)
                #     cv2.imshow("Taiko Rehab", img)  # open pose img
                #     cv2.moveWindow("Taiko Rehab", 0, 0)
                #     cv2.resizeWindow("Taiko Rehab", int(1536/2), int(864))
                #     first = False
                # else:
                #     cv2.imshow("Taiko Rehab", img)  # open pose img

                cv2.imshow("Taiko Rehab", img)  # open pose img
                key = cv2.waitKey(1)
                if key == 27  or key & 0xFF == ord('q') or key & 0xFF == ord('Q'):   # ESC or q to exit
                    break
                elif key & 0xFF == ord('p') or key & 0xFF == ord('P') :  # IF 'p' or 'P' start midi song 
                    self.video.start()
                    self.midi.start()

            
        finally:
            print('Saving logs....')
            self.cam.stop()
            self.armsPos.logOnDisk()
            # FOR MULTIUSER (DEPRECATED)
            # for i in range(0,self.joy.jCount):
            #     self.m5[i].stop()  # Logs force readings when stopped
            self.m5.stop()
            self.joy.stop()   # No need to log 
            self.midi.stop()  
            self.video.stop()
            self.midi.logOnDisk()  # logs midi and joystick hit events     
            
            # FOR MULTIPLE USER (DEPRECATED)
            # TODO Join logs for each joystick
            # for i in range(0,self.joy.jCount):
            #     time.sleep(2) 
            #     print (self.m5[i].log_file)
            #     self.armsPos.joinCsvLogs( self.m5[i].log_file, self.midi.log_file, self.armsPos.log_file, FULL_LOG_FILE )
            
            # SAVE ALL LOGS IN A SINGLE FILE (SINGLE USER ONLY)
            self.armsPos.joinCsvLogs( self.m5.log_file, self.midi.log_file, self.armsPos.log_file, FULL_LOG_FILE )

            print('Taiko Rehab has stopped....  Bye bye ( n o n ) p ')
            sys.exit(-1)
            return

    # except Exception as e:
    #     print(e)
    #     sys.exit(-1)

if __name__ == "__main__":
    main()


