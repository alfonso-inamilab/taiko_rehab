# INSTRUCTTIONS TAKEN FROM HERE:
# https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/01_demo.md#running-on-images-video-or-webcam


# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
from sys import platform
import argparse

OP_MODELS_PATH = "C:/openpose/openpose/models/" # OpenPose models folder 
OP_PY_DEMO_PATH = "C:/openpose/openpose/build/examples/tutorial_api_python/" # OpenPose demo folder 

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = OP_PY_DEMO_PATH
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(dir_path + '/../../python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
            import pyopenpose as op
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python');
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    # Flags
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_path", default="../../../examples/media/COCO_val2014_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
    # parser.add_argument("--video", default=" C:/rehab/src/taiko_rehab/src/samples/sample1.mp4 ")
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = OP_MODELS_PATH
    params["video"] = "C:/rehab/src/taiko_rehab/src/samples/sample1.mp4"
    params["write_json"]  = "./jsons/"
    # params["hand"] = True


    # Add others in path?
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

    # Construct it from system arguments
    # op.init_argv(args[1])
    # oppython = op.OpenposePython()

    print (params)
    # Starting OpenPose
    opWrapper = op.WrapperPython(op.ThreadManagerMode.Synchronous)
    opWrapper.configure(params)
    opWrapper.execute()
except Exception as e:
    print(e)
    sys.exit(-1)