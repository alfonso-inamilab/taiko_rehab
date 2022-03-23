# INSTRUCTTIONS TAKEN FROM HERE:
# https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/01_demo.md#running-on-images-video-or-webcam

# EXTRACTION USING OPENPOSE VIDEO PROCESSING AND SAVING THE POSES IN A SINGLE CSV FILE
# It requires OpenCV installed for Python
import sys
import cv2
import csv
import json
import os
from os import listdir
from os.path import isfile, join
from sys import platform
# import argparse

from include.globals import OP_PY_DEMO_PATH
from include.globals import OP_MODELS_PATH

class VideoProcess():

    def __init__(self):
        pass

    # PROCESS THE VIDEO IN OPENPOSE VIDEO FUNCTION (FRAME BY FRAME !!)
    # EXTRACT THE POSES IN JSON AND THEN SAVE THEM IN A JSON FILE
    # ONLY WORKS FOR SINGLE USER. 
    def process_video(self, video_path, save_csv_path ):
        sys.path.append(OP_PY_DEMO_PATH + '/../../python/openpose/Release')
        os.environ['PATH']  = os.environ['PATH'] + ';' + OP_PY_DEMO_PATH + '/../../x64/Release;' +  OP_PY_DEMO_PATH + '/../../bin;'
        import pyopenpose as op

        jsons_path = "./include/jsons/"

        # Custom Params (refer to include/openpose/flags.hpp for more parameters)
        params = dict()
        params["model_folder"] = OP_MODELS_PATH
        params["video"] = video_path
        params["write_json"]  = jsons_path
        # params["hand"] = True

        # DELETE PREVIOUS CSV FILES CREATED
        onlyfiles = [f for f in listdir(jsons_path) if isfile(join(jsons_path, f))]
        for ftrash in onlyfiles:
            name, ext = os.path.splitext(ftrash)
            if (ext == '.json'):
                print("Deleting old JSON file", os.path.join(jsons_path, ftrash) )
                os.remove(os.path.join(jsons_path, ftrash))

        opWrapper = op.WrapperPython(op.ThreadManagerMode.Synchronous)
        opWrapper.configure(params)
        opWrapper.execute()

        # CREATE THE CSV FILE AFTER THE OPENCV EXTRANCTION FINISHES
        # TIMESTAMP WILL BE CALCULATED USING THE FRAME NUMBER (indicated in the CSV file name)
        onlyfiles = [f for f in listdir(jsons_path) if isfile(join(jsons_path, f))]
        onlyfiles = sorted(onlyfiles)

        with open(save_csv_path, 'w',  newline='') as csvfile:
            writer = csv.writer(csvfile)
            fcount = 1
            for new_file in onlyfiles:
                name, ext = os.path.splitext(new_file)
                if (ext == '.json'):
                    
                    f = open (os.path.join(jsons_path, new_file), "r")
                    data = json.loads(f.read())

                    # save pose data in to a single csv file
                    # in case there is nobody in the scene only add zeros  
                    pose_data = []
                    if not data["people"]:
                        print ("Nobody found in frame ", fcount)
                        pose_data = [0] * 75
                    else:  # if a "valid" pose is found (this could also be an openpose miss detection... ) 
                        # print ("saving frame ", fcount)
                        for point in  data["people"][0]["pose_keypoints_2d"] :
                            pose_data.append(point)
                              
                    writer.writerow(pose_data)  
                    fcount = fcount + 1  #ONLY used for debug and error message        
            csvfile.close()

        print ("Video pre-process has finished. ( n - n ) p")
        sys.exit(-1)
        return
        
    
# vp = VideoProcess()
# vp.process_video("C:/rehab/src/taiko_rehab/src/samples/sample1.mp4", "C:/rehab/src/taiko_rehab/src/samples/pinchixxx.csv")


