# Example to use a webcam with OpenCV Demo for python. 
# TODO Get (aproximate) the arms velocity
# TODO Implement taiko joystick wcontrols
# TODO MIDI audio synthesizer 

import sys
import cv2
import os
import time
from sys import platform
import argparse

# TAIKO REHAB MODULES
from cameraThread import camThread

# GLOBAL VARIABLES 
OP_MODELS_PATH = "C:\\openpose\\openpose\\models\\" # OpenPose models folder
OP_PY_DEMO_PATH = "C:\\openpose\\openpose\\build\\examples\\tutorial_api_python\\"  # OpenPose 
CAM_OPCV_ID = 1  # Open CV camera ID

try:
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
    cam = camThread(1, 90)  # Init camera thread object
    cam.start()   # Start camera capture

    try:
        while True:
            start = time.time()
            img = cam.get_video_frame()  #rgb right camera
            if img is None:
                continue
            
            datum.cvInputData = img
            opWrapper.emplaceAndPop(op.VectorDatum([datum]))

            # print("Body keypoints: \n" + str(datum.poseKeypoints))
            cv2.imshow("OpenPose 1.7.0 - Rehab", datum.cvOutputData)
            key = cv2.waitKey(15)
            if key == 27  or key & 0xFF == ord('q'):   # ESC or q to exit
                break

            end = time.time()
            # print("Frame total time: " + str(end - start) + " seconds")  # DEBUG
    finally:
       print('Taiko rehab as stopped....  Bye bye ( n o n ) p ')
       cam.stop()

except Exception as e:
    print(e)
    sys.exit(-1)
