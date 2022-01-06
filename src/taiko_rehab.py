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
import numpy as np
from multiprocessing import Array

# TAIKO REHAB MODULES
from cameraThread import camThread
# PYGAME JOYSTICK TO CATCH TIME EVENTS
from joystick import Joystick
# MIDO TO PLAY MIDI AND MEASURE TIMMING
from midi_control import MidiControl
# CLASS TO CALCULATE AND LOG WRIST POSITION
from arm_angle_logger import ArmAngleLog
# CLASS TO READ THE FORCE/ACC FROM THE SENSOR
from m5stick_serial_acc import M5SerialCom

# OPENCV GLOBAL VARIABLES 
OP_MODELS_PATH = "C:\\openpose\\openpose\\models\\" # OpenPose models folder
OP_PY_DEMO_PATH = "C:\\openpose\\openpose\\build\\examples\\tutorial_api_python\\"  # OpenPose 
CAM_OPCV_ID = 1    # Open CV camera ID   (IS NOT USED ANYMORE)
MAX_TXT_FRAMES = 5  # Number of frames the text wrist will be in the screen
MAX_NUM_PEOPLE = 1  # Nuber of users detected with OpenCV. -1 for No limit

# PROGRAM GLOBAL VARIABLES
FULL_LOG_FILE = 'full_log.csv'
FORCE_LOG_NAME = 'force_log_' 
WRIST_LOG_NAME = 'wrist_angle_log.csv'


def main():
# try:
    # Import Openpose (Windows)
    dir_path = OP_PY_DEMO_PATH
    try:       
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append(dir_path + '/../../python/openpose/Release');
        os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
        import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    # Flags
    parser = argparse.ArgumentParser()
    # parser.add_argument("--image_path", default="../../../examples/media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = OP_MODELS_PATH
    params["number_people_max"] = MAX_NUM_PEOPLE
    # params["num_gpu"] = 1
    # params["camera"] = CAM_OPCV_ID
    # params["identification"] = True

    # Add other arguments in the path 
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1])-1: next_item = args[1][i+1]
        else: next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-','')
            if key not in params:  params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-','')
            if key not in params: params[key] = next_item
  
    # Check if the MIDI file path is given in the arguments
    if not args[1]:
        print ("ERROR: MIDI file path is missing.")
        return
    if os.path.isfile(args[1][0]) is False:
        print ("ERROR: " + str(args[1][0]) + " is not a MIDIfile.")
        return 
    ext = os.path.splitext(args[1][0])[1] 
    if ext != '.mid' and ext != '.midi':
        print ("ERROR: The file is not a valid MIDI file.")
        return

    # Init OpenPose python wrapper
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()
    datum = op.Datum()

    # Init camera thread
    # cap = cv2.VideoCapture(CAM_OPCV_ID, cv2.CAP_DSHOW)
    cam = camThread(CAM_OPCV_ID, 200)  # Init camera thread object
    cam.start()   # Start camera capture

    # Init Joystick       
    joy = Joystick()
    joyTime = Array('q', [0] * joy.jCount)  # Sync object to save the joystick number and timming
    joy.start(joyTime)   # Init thread and start joystick event catch thread

    # Init M5 acc serial thread
    joyForces = Array('f', [0] * joy.jCount)  # object to save the joysitck hit force
    m5 = []
    for i in range(0,joy.jCount):
        m5.append( M5SerialCom( bauds=115200, port='COM5', joyForces=joyForces, joyIndex = i, log_file=FORCE_LOG_NAME+str(i)+'.csv') )
        m5[-1].start()

    # Init MIDI control process
    midi = MidiControl(portname=None, channel=0, filename=args[1][0], joyTime=joyTime, joyForces=joyForces, numJoysticks=joy.jCount)

    # Logs the users' wrists positions
    wristPos = ArmAngleLog(cam.resX, cam.resY, log_file=WRIST_LOG_NAME)

    txtFrames = MAX_TXT_FRAMES  # Number of cycles the wrist text appears on the screen
    hit_vel = 0   # To print the velocity on the screen
    hit_ok = False  # To print the hit miss or fail on the screen
    try:
        while True:
            start = time.time()
            img = cam.get_video_frame()  #rgb right camera
            if img is None:
                continue
            
            datum.cvInputData = img
            opWrapper.emplaceAndPop(op.VectorDatum([datum]))

            # Estimate the velocity of the wrist from the poseKeypoints
            if datum.poseKeypoints is not None:
                events = midi.isNewEvent()
                img = datum.cvOutputData
                img = wristPos.drawPersonNum(img, datum.poseKeypoints)
                wristPos.logArmAngleVelocity(datum.poseKeypoints)
                if events:  
                    txtFrames = 0

                    if txtFrames < MAX_TXT_FRAMES:
                        img = wristPos.drawHit(img, events, datum.poseKeypoints)    # Draws if hit were OK or NOT
                        txtFrames = txtFrames + 1

                cv2.imshow("Taiko Rehab", img)
                key = cv2.waitKey(15)
                if key == 27  or key & 0xFF == ord('q'):   # ESC or q to exit
                    break
                elif key & 0xFF == ord('p') or key & 0xFF == ord('P') :  # IF 'p' or 'P' start midi song 
                    midi.start()

            end = time.time()
            # print("Frame total time: " + str(end - start) + " seconds")  # DEBUG
    finally:
        print('Saving logs....')
        cam.stop()
        wristPos.logOnDisk()
        for i in range(0,joy.jCount):
            m5[i].stop()  # Logs force readings when stopped
        joy.stop()   # No need to log 
        midi.stop()  
        midi.logOnDisk()  # logs midi and joystick hit events     
        
        # TODO Join logs for each joystick
        for i in range(0,joy.jCount):
            time.sleep(2)
            print (m5[i].log_file)
            wristPos.joinCsvLogs( m5[i].log_file, midi.log_file, wristPos.log_file, FULL_LOG_FILE )
        print('Taiko Rehab has stopped....  Bye bye ( n o n ) p ')

# except Exception as e:
#     print(e)
#     sys.exit(-1)

if __name__ == "__main__":
    main()


