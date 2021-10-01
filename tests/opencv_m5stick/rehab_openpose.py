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
# UDP M5STICK-C SERVER   
# from m5stick_udp_server import M5StickUDP
# PYGAME JOYSTICK TO CATCH TIME EVENTS
from joystick import Joystick
# MIDO TO PLAY MIDI AND MEASURE TIMMING
from midi_control import MidiControl
# CLASS TO CALCULATE AND LOG WRIST POSITION
from wrist_pos_logger import OPWristPos
# CLASS TO READ THE FORCE/ACC FROM THE SENSOR
from m5stick_serial_acc import M5SerialCom

# GLOBAL VARIABLES 
OP_MODELS_PATH = "C:\\openpose\\openpose\\models\\" # OpenPose models folder
OP_PY_DEMO_PATH = "C:\\openpose\\openpose\\build\\examples\\tutorial_api_python\\"  # OpenPose 
CAM_OPCV_ID = 0    # Open CV camera ID   (IS NOT USED ANYMORE)
MAX_TXT_FRAMES = 5  # Number of frames the text wrist will be in the screen


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
    # params["num_gpu"] = 1
    # params["camera"] = CAM_OPCV_ID

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

    # Init OpenPose python wrapper
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()
    datum = op.Datum()

    # Init camera thread
    # cap = cv2.VideoCapture(CAM_OPCV_ID, cv2.CAP_DSHOW)
    cam = camThread(CAM_OPCV_ID, 200)  # Init camera thread object
    cam.start()   # Start camera capture

    # Init UDP server thread 
    # m5 = M5StickUDP(port=50007, dt=10, buffer_size=1000, log_file='m5log.csv')
    # m5.start()   # Star UDP server 

    # Init Joystick       
    joy = Joystick()
    joyTime = Array('q', [0] * joy.jCount)  # Sync object to save the joystick number and timming
    joy.start(joyTime)   # Init thread and start joystick event catch thread

    # Init M5 acc serial thread
    joyForces = Array('f', [0] * joy.jCount)  # object to save the joysitck hit force
    m5 = []
    for i in range(0,joy.jCount):
        m5.append( M5SerialCom( bauds=115200, port='COM3', joyForces=joyForces, joyIndex = i, log_file='acc_log.csv') )
        m5[-1].start()

    # Init MIDI control process
    midi = MidiControl(portname=None, channel=0, filename='mary_lamb.mid', joyTime=joyTime, joyForces=joyForces, numJoysticks=joy.jCount)
    # midi.start()  # Start midi control PROCESS

    # Logs the users' wrists positions
    wristPos = OPWristPos(cam.resX, cam.resY, log_file='wrist_pos_log.csv')

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
                if events is not None:  
                    w_pos = wristPos.getWristElevation(datum.poseKeypoints)
                    txtFrames = 0

                img = datum.cvOutputData
                img = wristPos.drawPersonNum(img, datum.poseKeypoints)
                if txtFrames < MAX_TXT_FRAMES and events is not None:
                    img = wristPos.drawHitOK(img, events, datum.poseKeypoints)    # Draws if hit were OK or NOT
                    txtFrames = txtFrames + 1

                cv2.imshow("Taiko Rehab", img)
                key = cv2.waitKey(15)
                if key == 27  or key & 0xFF == ord('q'):   # ESC or q to exit
                    break
                elif key & 0xFF == ord('p'):
                    midi.start()

            end = time.time()
            # print("Frame total time: " + str(end - start) + " seconds")  # DEBUG
    finally:
       print('Taiko rehab as stopped....  Bye bye ( n o n ) p ')
       cam.stop()
       for i in range(0,joy.jCount):
           m5[i].stop()
       joy.stop()
       midi.stop()


if __name__ == "__main__":
    main()

# except Exception as e:
#     print(e)
#     sys.exit(-1)
