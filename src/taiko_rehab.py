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
from multiprocessing import Array, Value


# IMPORTING GLOBAL PARAMETERS 
from include.globals import OP_PY_DEMO_PATH
from include.globals import OP_MODELS_PATH
from include.globals import CAM_OPCV_ID
from include.globals import MAX_NUM_PEOPLE
from include.globals import MAX_TXT_FRAMES

from include.globals import FULL_LOG_FILE
from include.globals import ARMS_LOG_NAME
from include.globals import FORCE_LOG_NAME

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
    # if not args[1]:
    #     print ("ERROR: MIDI file path is missing.")
    #     return
    # if os.path.isfile(args[1][0]) is False:
    #     print ("ERROR: " + str(args[1][0]) + " is not a MIDIfile.")
    #     return 
    # # if ext == '.mp4':
    # #     video = VideoDisplay( args[1][0], None, 0)
    # #     video.video_pre_proc(OP_PY_DEMO_PATH)
    # #     return
    # if ext != '.mid' and ext != '.midi':
    #     print ("ERROR: The file is not a valid MIDI or MP4 file.")
    #     return

    # Check parameters for video preprocessing 
    if args[1][0] == '-p':
        ext = os.path.splitext(args[1][1])[1]
        if ext == 'mp4':
            print ("Preprocsign the video....");   print ("Generating CSV file.... ")
            video = VideoDisplay( args[1][1], None, 0)
            video.video_pre_proc(OP_PY_DEMO_PATH)
            return

    # Check parameters for midi file 
    if not args[1][0]:
        print ("ERROR: MIDI file path is missing.")
        return
    if os.path.isfile(args[1][0]) is False:
        print ("ERROR: " + str(args[1][0]) + " is not a file.")
        return  
    ext = os.path.splitext(args[1][0])[1]
    if ext != '.mid' and ext != '.midi':
        print ("ERROR: The file is not a valid MIDI or MP4 file.")
        return   
    
    # Check paramters for video file 
    if not args[1][1]:
        print ("ERROR: MIDI file path is missing.")
        return
    if os.path.isfile(args[1][1]) is False:
        print ("ERROR: " + str(args[1][1]) + " is not a file.")
        return  
    ext = os.path.splitext(args[1][1])[1]
    if ext != '.mp4' and ext != '.mp4':
        print ("ERROR: The file is not a valid MIDI or MP4 file.")
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

    timestamp = Value('i', 0)
    video = VideoDisplay( args[1][1], timestamp, 200)  # video display 

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

    # Logs the users' arms positions
    video_name = os.path.splitext(args[1][1])[0]
    armsPos = ArmAngleLog(cam.resX, cam.resY, video_name + ".csv", log_file=ARMS_LOG_NAME)

    txtFrames = MAX_TXT_FRAMES  # Number of cycles hit feedback appears on the screen
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

            # Estimate the position and velocity of the arms and shoulders
            if datum.poseKeypoints is not None:
                events = midi.isNewEvent()
                # img = datum.cvOutputData  # OpenCV skeleton image 
                img = armsPos.drawPersonNum(img, datum.poseKeypoints)
                # calcs the arm and shoulder angular velocity
                armsPos.calcArmVel(datum.poseKeypoints)
                # Checks if the users arms and instructors arms (video) match
                arms_matches = armsPos.getArmsMatch(timestamp, 0.8) # must be called after calcArmVel
                # Draws the skeleton of the user's arms (changes accordingly to match)
                armsPos.drawSkeleton(img, datum.poseKeypoints, arms_matches)
                if events:  
                    txtFrames = 0

                    if txtFrames < MAX_TXT_FRAMES:
                        img = armsPos.drawHit(img, events, datum.poseKeypoints)    # Draws if hit were OK or NOT
                        txtFrames = txtFrames + 1

            end = time.time()
            # print("Frame total time: " + str(end - start) + " seconds")  # DEBUG
        
            img = cv2.resize(img, ((int)(img.shape[1]*0.5), (int)(img.shape[0]*0.5)) , interpolation = cv2.INTER_AREA  )
            cv2.imshow("Taiko Rehab", img)  # open pose img
            key = cv2.waitKey(1)
            if key == 27  or key & 0xFF == ord('q'):   # ESC or q to exit
                break
            elif key & 0xFF == ord('p') or key & 0xFF == ord('P') :  # IF 'p' or 'P' start midi song 
                video.start()
                midi.start()

           
    finally:
        print('Saving logs....')
        cam.stop()
        armsPos.logOnDisk()
        for i in range(0,joy.jCount):
            m5[i].stop()  # Logs force readings when stopped
        joy.stop()   # No need to log 
        midi.stop()  
        video.stop()
        midi.logOnDisk()  # logs midi and joystick hit events     
        
        # TODO Join logs for each joystick
        for i in range(0,joy.jCount):
            time.sleep(2)
            print (m5[i].log_file)
            armsPos.joinCsvLogs( m5[i].log_file, midi.log_file, armsPos.log_file, FULL_LOG_FILE )
        print('Taiko Rehab has stopped....  Bye bye ( n o n ) p ')

# except Exception as e:
#     print(e)
#     sys.exit(-1)

if __name__ == "__main__":
    main()


