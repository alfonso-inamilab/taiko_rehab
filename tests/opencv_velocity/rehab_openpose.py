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

# TAIKO REHAB MODULES
from cameraThread import camThread

# GLOBAL VARIABLES 
OP_MODELS_PATH = "C:\\openpose\\openpose\\models\\" # OpenPose models folder
OP_PY_DEMO_PATH = "C:\\openpose\\openpose\\build\\examples\\tutorial_api_python\\"  # OpenPose 
CAM_OPCV_ID = 0  # Open CV camera ID   (IS NOT USED ANYMORE)

# VARIABLES AND INITS FOR THE JOYSTICK EVENTS
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

# VARAIBLES FOR VELOCITY CALCULATION

p_left = [0, 0]
p_right = [0, 0]
v_left = [0, 0]
v_right = [0, 0]
MAX_VEL =0 
ret_vel = [0,0]
prev_avel_left = 0
prev_avel_right = 0
RIGHT_ARM_LEN = 0
LEFT_ARM_LEN = 0

first = True
now = time.time_ns()
past = 0
ude_pos_left = [0,0]
ude_pos_right = [0,0]
ude_diff_left = [0,0]
ude_diff_right = [0,0]
def getVelocity(pose):
    global past; global now; global first
    global ude_pos_left; global ude_pos_right
    global ude_diff_left; global ude_diff_right

    past = now
    now = int( round(time.time() * 1000 ))   # ORIGINAL int( round(time.time() * 1000))
    if first:
        # left wrist position
        ude_pos_left[0] = pose[7][0]-pose[6][0]
        ude_pos_left[1] = pose[7][1]-pose[6][1] 
        # right wrist position
        ude_pos_right[0] = pose[4][0]-pose[3][0]
        ude_pos_right[1] = pose[4][1]-pose[3][1] 

        first = False
    elif not first :
        # get time 
        dt = now - past 

        # CALCULATE HAND ANGULAR VELOCITY       
        ude_diff_left[0] =  (ude_pos_left[0] - (pose[7][0]-pose[6][0])) 
        ude_diff_left[1] =  (ude_pos_left[1] - (pose[7][1]-pose[6][1])) 
        ude_diff_right[0] = (ude_pos_right[0] - (pose[4][0]-pose[3][0])) 
        ude_diff_right[1] = (ude_pos_right[1] - (pose[4][1]-pose[3][1])) 

        # LINEAL VELOCITY (non normalized)
        ret_vel[0] = math.sqrt( (ude_diff_left[0]*ude_diff_left[0]) + (ude_diff_left[1]*ude_diff_left[1]) ) / dt
        ret_vel[1] = math.sqrt( (ude_diff_right[0]*ude_diff_right[0]) + (ude_diff_right[1]*ude_diff_right[1]) ) / dt

        # left wrist position
        ude_pos_left[0] = pose[7][0]-pose[6][0]
        ude_pos_left[1] = pose[7][1]-pose[6][1] 
        # right wrist position
        ude_pos_right[0] = pose[4][0]-pose[3][0]
        ude_pos_right[1] = pose[4][1]-pose[3][1] 

        taiko = getJoystickEvent(0)

        # PRINT ANGULAR VELOCITY 
        # print ( "{:.5f}".format(avel_left) + "," +  "{:.5f}".format(avel_right) + "," + str(taiko[0]) + "," + str(taiko[1]) + "," )

        # PRINT POSE 
        # print ( "{:.5f}".format(p_left[0]) + "," +  "{:.5f}".format(p_left[1]) + "," , end = '' )
        # print ( "{:.5f}".format(p_right[0]) + "," +  "{:.5f}".format(p_right[1]) + "," )

        # PRINT DIRECT 1D WRIST VELOCITY
        print ( "{:.5f}".format(ret_vel[0]) + "," +  "{:.5f}".format(ret_vel[1]) + "," + str(taiko[0]) + "," + str(taiko[1]) + "," )

        # PRINT VELOCITY VALUES 
        # print (  "{:.5f}".format(v_left[0]) +","+  "{:.5f}".format(v_left[1]) +"," + "{:.5f}".format(v_left[2]) + "," , end='' )
        # print (  "{:.5f}".format(v_right[0]) +","+  "{:.5f}".format(v_right[1]) +"," + "{:.5f}".format(v_right[2]) + ","  )
        
        # Velocity MIDI Normalization (0-255)
        # v_left[0] = (v_left[0]*255)/MAX_VEL;  v_left[1] = (v_left[1]*255)/MAX_VEL;    v_left[2] = (v_left[2]*255)/MAX_VEL
        # v_right[0] = (v_right[0]*255)/MAX_VEL;  v_right[1] = (v_right[1]*255)/MAX_VEL;    v_right[2] = (v_right[2]*255)/MAX_VEL

        # PRINT NORMALIZED VELOCITY 
        # print (  "{:.5f}".format(ude_diff_left[0]) +","+  "{:.5f}".format(ude_diff_left[1]) +"," + str(taiko[0]) + "," + str(taiko[1]) + ",", end='' )
        # print (  "{:.5f}".format(ude_diff_right[0]) +","+  "{:.5f}".format(ude_diff_right[1]) +"," + str(taiko[0]) + "," + str(taiko[1]) + ","  )
    return ret_vel

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
    print (dir_path)
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
                estimateVelocity(datum.poseKeypoints[0])

                cv2.imshow("OpenPose 1.7.0 - Rehab Heels", datum.cvOutputData)
                key = cv2.waitKey(15)
                if key == 27  or key & 0xFF == ord('q'):   # ESC or q to exit
                    break


            end = time.time()
            # print("Frame total time: " + str(end - start) + " seconds")  # DEBUG
    finally:
       print('Taiko rehab as stopped....  Bye bye ( n o n ) p ')
       cam.stop()


if __name__ == "__main__":
    main()

# except Exception as e:
#     print(e)
#     sys.exit(-1)
