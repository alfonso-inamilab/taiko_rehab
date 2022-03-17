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
from datetime import datetime
import pygame
import numpy as np
from multiprocessing import Array, Value, Event

# IMPORTING GLOBAL PARAMETERS 
from include.globals import OP_PY_DEMO_PATH
from include.globals import OP_MODELS_PATH
from include.globals import CAM_OPCV_ID
from include.globals import MAX_TXT_FRAMES
from include.globals import DRAW_SENSEI_ARMS
from include.globals import DRAW_HITS
from include.globals import JOY_BUFF_SIZE


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
# CLASS TO PRE-PROCESS THE INSTRUCTORS VIDEO AND CREATE A CSV WITH THE POSES
from include.video_process import VideoProcess

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
        self.joyTimeBuf = None  # joystick pressing time event buffer
        self.joy_log = None  # logs all the joystick press events
        self.jBufIndx = None   # joystick event round buffer index
        self.joyForces = None # saves the joystick hit force
        self.txtFrames = None # Number of cycles hit feedback appears on the screen
        self.hit_vel = None   # To print the velocity on the screen
        self.hit_ok = None  # To print the hit miss or fail on the screen
        self.first = None # To detect the first process cycle
        self.start_event = None   # Event to syn the video and midi players
        self.timestamp = None
    
    # sets the default path and gets the number of the lats pic 
    def setRootPath(self, path=""):
        if path == "":
            self.rootPath = os.getcwd() + os.path.sep + "captures" # default is current dictory + captures
            if os.path.isdir(self.rootPath) == False:
                os.mkdir(self.rootPath) #create folder if do not exists
        else:
            self.rootPath = rootPath

    # create a new folder path, to save the log files
    def getNewFolder(self, prefix="taiko_log_"):
        # Get root path directory 
        rootPath = os.getcwd() + os.path.sep + "logs" 
        if os.path.isdir(rootPath) == False:
            os.mkdir(rootPath) #create folder if do not exists

        #get date and time
        now = datetime.now()
        today = now.strftime("%Y%m%d")
        hour = now.strftime("%H%M")

        newFolder = rootPath + os.path.sep + prefix + today + "_" + hour + "_"
        counter = 1
        retVal = ""
        while True:
            retVal = newFolder + format(counter, '02d') 
            if os.path.isdir(retVal) == False:
                os.mkdir(retVal)
                break
            else:
                counter = counter + 1
        return retVal 


    def initThreads(self,  csv_path, video_path, midi_path, start_frame):
        # try:
            joyOK = True;  m5OK = True;   # Variables to check it the sensors, joystick and camera are connected
            log_path = self.getNewFolder()

            # Init camera thread
            # cap = cv2.VideoCapture(CAM_OPCV_ID, cv2.CAP_DSHOW)
            self.cam = camThread(CAM_OPCV_ID, 200)  # Init camera thread object
            self.cam.start()   # Start camera capture

            self.start_event = Event()
            self.timestamp = Value('q', 0)
            self.video = VideoDisplay( video_path, self.timestamp, 200, self.start_event, start_frame, video_scale=1.0 )  # video display 
            
            # Init Joystick       
            self.joy = Joystick()
            self.joyTimeBuf = Array('q', [0] * JOY_BUFF_SIZE)  # Buf that saves the last joystick events (10 items is enough)
            self.jBufIndx = Value('q', 0)  # index value for the joystick entry buffer
            self.joy_log = Array ('q', [0] * JOY_BUFF_SIZE)
            self.joy.start('Microsoft GS Wavetable Synth 0', self.joyTimeBuf, self.jBufIndx, self.joy_log)   # Init thread and start joystick event catch thread
            joyOK = self.joy.joystickCheck()   # true if the joystick is connected to the PC

            # Init M5 acc serial thread
            self.joyForces = Array('f', [0] * self.joy.jCount)  # object to save the joysitck hit force
            
            # M5 stick control class init
            self.m5 = M5SerialCom( bauds=115200, joyForces=self.joyForces, joyIndex = 0, log_path=log_path)
            self.m5.start()
            m5OK = self.m5.m5Check()   # true if m5 is connected to the PC

            # Init MIDI control process
            self.midi = MidiControl(portname='Microsoft GS Wavetable Synth 0', log_path=log_path, filename=midi_path, joyTimeBuf=self.joyTimeBuf, jBufIndx=self.jBufIndx, start_event=self.start_event, joy_log=self.joy_log, timestamp=self.timestamp)

            # Logs the users' arms positions
            self.armsPos = ArmAngleLog(self.cam.resX, self.cam.resY, csv_path, log_path=log_path)

            self.txtFrames = MAX_TXT_FRAMES  # Number of cycles hit feedback appears on the screen
            self.hit_vel = 0   # To print the velocity on the screen
            self.hit_ok = False  # To print the hit miss or fail on the screen
            self.first = True # To detect the first process cycle

            return [joyOK, m5OK]  # returns the connection checks to inform the user if something went wrong

        # except Exception as e:
        #     print(e)
        #     sys.exit(-1)

    def videoPreProcess(self, video_path, save_csv_path):
        vp = VideoProcess()
        vp.process_video(video_path, save_csv_path)


    def startTraining(self):
        # try:
        # Import Openpose (Windows)
        try:       
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(OP_PY_DEMO_PATH + '/../../python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + OP_PY_DEMO_PATH + '/../../x64/Release;' +  OP_PY_DEMO_PATH + '/../../bin;'
            import pyopenpose as op
        except ImportError as e:
            print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
            raise e


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

        window_name = "Taiko Rehab"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        # start = 0
        # img = None 
        # events = None
        # arms_matches = None
        # end = 0
        while True:
            # start = int(time.time_ns() / 1000000)
            img = self.cam.get_video_frame()  #rgb right camera
            if img is None:
                continue

            self.datum.cvInputData = img
            self.opWrapper.emplaceAndPop(op.VectorDatum([self.datum]))

            # Estimate the position and velocity of the arms and shoulders
            if self.datum.poseKeypoints is not None:
                event = self.midi.isNewEvent()  # Checks if the last note was hit or not

                # Draws the user ID over his head
                # img = self.armsPos.drawPersonNum(img, self.datum.poseKeypoints)  #DEBUG ONLY
                
                # Calcs the arm and shoulder angular velocity 
                self.armsPos.logArmsVel(self.datum.poseKeypoints)
                self.armsPos.logArmsHeight(self.datum.poseKeypoints)
                
                # Draws the skeleton of the user's arms (changes color accordingly to match)
                # self.armsPos.drawSkeleton(img, self.datum.poseKeypoints, arms_matches, 0.8)

                # Draws sensei's arms over the user
                if DRAW_SENSEI_ARMS:
                    # Checks if the users arms and instructors arms (video) match
                    arms_matches = self.armsPos.getArmsMatch(self.video.get_timestamp(), self.video.get_fps(), 0.8) # must be called after logArmsVel
                    img = self.armsPos.drawSenseiArms(img, self.datum.poseKeypoints, arms_matches, self.video.get_timestamp(), self.video.get_fps(), 0.8)
                
                if event[0] == True:  
                    self.txtFrames = 0   # Init the frame counter for the visual feedback
                    self.midi.eventFinished()  # Turn off the event flag

                # HIT visual feedback
                if self.txtFrames < MAX_TXT_FRAMES and DRAW_HITS: 
                    img = self.armsPos.drawHit(img, event, self.datum.poseKeypoints)    # Draws if hit were OK or NOT
                    self.txtFrames = self.txtFrames + 1


            # img = cv2.resize(img, ((int)(img.shape[1]*0.5), (int)(img.shape[0]*0.5)) , interpolation = cv2.INTER_AREA  )
            # if first:
            #     cv2.namedWindow("Taiko Rehab", cv2.WINDOW_NORMAL)
            #     cv2.imshow("Taiko Rehab", img)  # open pose img
            #     cv2.moveWindow("Taiko Rehab", 0, 0)
            #     cv2.resizeWindow("Taiko Rehab", int(1536/2), int(864))
            #     first = False
            # else:
            #     cv2.imshow("Taiko Rehab", img)  # open pose img

            cv2.imshow(window_name, img)  # open pose img
            key = cv2.waitKey(1)
            if key == 27  or key & 0xFF == ord('q') or key & 0xFF == ord('Q'):   # ESC or q to exit
                break
            elif key & 0xFF == ord('p') or key & 0xFF == ord('P') :  # IF 'p' or 'P' start midi song 
                self.video.start()
                self.midi.start()

                

            # end = int(time.time_ns() / 1000000)
            # print("Frame total time: " + str(end - start) + " milliseconds")  # DEBUG

            
        # finally:
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
        # self.midi.logOnDisk()  # logs midi and joystick hit events     
        
        # FOR MULTIPLE USER (DEPRECATED)
        # TODO Join logs for each joystick
        # for i in range(0,self.joy.jCount):
        #     time.sleep(2) 
        #     print (self.m5[i].log_file)
        #     self.armsPos.joinCsvLogs( self.m5[i].log_file, self.midi.log_file, self.armsPos.log_file, FULL_LOG_FILE )
        
        # SAVE ALL LOGS IN A SINGLE FILE (SINGLE USER ONLY)
        # joinCsvLogs( self.m5.log_file, self.midi.log_file, self.armsPos.log_file, FULL_LOG_FILE )

        print('Taiko Rehab has stopped....  Bye bye ( n o n ) p ')
        sys.exit(-1)
        return

    # except Exception as e:
    #     print(e)
    #     sys.exit(-1)


    # Joins all the CSV log files into a single file (Using Pandas)
    def joinCsvLogs(self, force_log_file, midi_log_file , arms_log_file, full_log_file ):
        # Open every CSV in a independent dataframe
        force = pd.read_csv(force_log_file, index_col=None, header=0)
        arms = pd.read_csv(arms_log_file, index_col=None, header=0)
        midi = pd.read_csv(midi_log_file, index_col=None, header=0)
        # Merge force and arms data frames
        force_arms = pd.concat([force,arms])
        force_arms = force_arms.sort_values('Time(epoch)')
        # Merge force arms and midi dataframes
        force_arms_midi =  pd.concat([force_arms, midi])
        force_arms_midi = force_arms_midi.sort_values('Time(epoch)')
        force_arms_midi = force_arms_midi.drop('Time_Lapse(ms)',1)   # Drop Time lapse it is not needed
        force_arms_midi.to_csv(full_log_file, index=False)   # Save on CSV file

if __name__ == "__main__":
    main()


