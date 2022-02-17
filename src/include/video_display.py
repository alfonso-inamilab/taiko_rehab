import cv2
import os
import csv
import math
import sys
import vlc
import numpy as np
from threading import Thread

# IMPORTING GLOBAL PARAMETERS (for OpenPose control)
from include.globals import OP_PY_DEMO_PATH
from include.globals import OP_MODELS_PATH
from include.globals import CAM_OPCV_ID
from include.globals import MAX_TXT_FRAMES

class VideoDisplay():

    def __init__(self, videopath, timestamp, deque_size, video_scale=1.0):
        self.get_frame_thread = Thread(target=self.get_frame, args=([timestamp]))

        self.play = False
        self.fps = 0
        self.length = 0
        self.video_time = -666
        self.player = None
        self.player = vlc.MediaPlayer(videopath)
        self.player.video_set_scale(video_scale)



    # Pre process the video and save the angular velocity of the instructor in a separate file
    # the craeted file saves the: [ frame number, right_elbow, right_shoulder, left_elbow, left_shoulder ]
    def video_pre_proc(self, videopath, save_csv_path):

        # Init OpenCV objects
        cap = cv2.VideoCapture(videopath)
        # Check if video can be open
        if cap.isOpened() == False:
            print("Error opening the instructor video file.")
        # Get video frame per seconds
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.f_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Get camera resolution 
        self.resX = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  
        self.resY = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)


        try:       
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(OP_PY_DEMO_PATH + '/../../python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + OP_PY_DEMO_PATH + '/../../x64/Release;' +  OP_PY_DEMO_PATH + '/../../bin;'
            import pyopenpose as op
        except ImportError as e:
            print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
            raise e

        params = dict()
        params["model_folder"] = OP_MODELS_PATH
        params["number_people_max"] = 1 #MAX_NUM_PEOPLE

        # Init OpenPose python wrapper
        opWrapper = op.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()
        datum = op.Datum()

        with open(save_csv_path, 'w',  newline='') as csvfile:
            writer = csv.writer(csvfile)  
            while (cap.isOpened()):            
                # Read next frame from stream and insert into deque
                ret, image = cap.read()  #uv camera
                if ret:
                    datum.cvInputData = image
                    opWrapper.emplaceAndPop(op.VectorDatum([datum])) 
                    
                    #  Get the vectors of the arms and shoulders
                    if datum.poseKeypoints is not None:
                        vectors = self.getArmsVectors(datum.poseKeypoints)
                        print(vectors)
                        img_out = datum.cvOutputData
                        cv2.imshow("Taiko Rehab", img_out)  # open pose img
                        key = cv2.waitKey(1)
                        if key == 27  or key & 0xFF == ord('q'):   # ESC or q to exit
                            break

                    timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
                    # [timestamp, left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]
                    writer.writerow( [timestamp, vectors[0][0], vectors[0][1],
                                                 vectors[1][0], vectors[1][1],
                                                 vectors[2][0], vectors[2][1],
                                                 vectors[3][0], vectors[3][1],
                                                 vectors[4][0], vectors[4][1],
                                                 vectors[5][0], vectors[5][1] ] )
                                  
                else:
                    break

            csvfile.close()
            cap.release()
            cv2.destroyAllWindows()

    # Returns the vectors of the shoulder, arm and forearm
    def getArmsVectors(self, poses):
        
        for i, pose in enumerate(poses): 
            # Calculate the rotation angle between the arm and forearm
            left_foream = np.array(  [ pose[7][0] - pose[6][0] , (self.resY - pose[7][1]) - (self.resY - pose[6][1])  ] )
            left_arm = np.array(  [ pose[5][0] - pose[6][0] ,    (self.resY - pose[5][1]) - (self.resY - pose[6][1])  ] )
            
            right_foream = np.array(  [ pose[4][0] - pose[3][0] , (self.resY - pose[4][1]) - (self.resY - pose[3][1] ) ] )
            right_arm = np.array(  [ pose[2][0] - pose[3][0] ,    (self.resY - pose[2][1]) - (self.resY - pose[3][1] ) ] )
            
            left_shoulder = np.array(  [ pose[1][0] - pose[5][0] , (self.resY - pose[1][1]) - (self.resY - pose[5][1])  ] )
            right_shoulder = np.array(  [ pose[1][0] - pose[2][0] , (self.resY - pose[1][1]) - (self.resY - pose[2][1])  ] )
        
        return [left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]

        
    # calcualtes the angle between two given vectors
    def calcVectorAngle(self, vector_1, vector_2):
        unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
        unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
        dot_product = np.dot(unit_vector_1, unit_vector_2)
        angle = np.arccos(dot_product)
        degs = (180.0/math.pi) * angle
        return degs
        
    # Starts the get frame thread
    def start(self):
        # Start background frame grabbing
        self.play = True
        self.player.play()
        self.get_frame_thread.start() 
        

    # Stops the reading frame thread
    def stop(self):
        self.play = False
        self.player.stop()


    def getHMSTime(self, millis):
        millis = int(millis)
        seconds=(millis/1000)%60
        frac = int ( (seconds % 1) * 1000) 
        seconds = int(seconds)
        minutes=(millis/(1000*60))%60
        minutes = int(minutes)
        hours=(millis/(1000*60*60))%24

        return ("%02d:%02d:%02d.%03d" % (hours, minutes, seconds, frac))

    # Get the frames for the 
    def get_frame(self, timestamp):
        while self.play:            
            self.length = self.player.get_length()
            self.video_time = self.player.get_time()
            timestamp.value = self.video_time
            # print (self.getHMSTime(self.video_time))

            # Check if the video finish playing
            if self.video_time >= self.length and (self.video_time !=0 and self.length !=0):
                print("Video finshed playing...")
                break

            
                