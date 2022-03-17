import time
import cv2
import os
import math
import csv
import pandas as pd
import numpy as np
from array import array
from threading import Thread



# Class that calculates the angle between the forearm and arm 
# and saves all the data in a log
class ArmAngleLog:

    def __init__(self, resX, resY, video_angles_file, log_path):
        self.log_file = log_path + os.path.sep + 'arms_log.csv'
        self.video_angles = None
        self.v_len = 0
        self.video_angles = self.initVideoArmPoses(video_angles_file)
        self.v_len = len(self.video_angles)
        self.resX = resX
        self.resY = resY
        self.INDEX_POS = 100
        self.SCORE_POS = 60
        self.armsLogs = []
        self.prev_time = 0
        self.video_angles_index = 0 # The search index of the instructor poses
        self.arms_hlog = []

        self.user_arms_pos = [0.0, 0.0, 0.0, 0.0]   # current arm/shoulder vector positions
        self.prev_arms_angle = [0.0, 0.0, 0.0, 0.0]   # last cycle arms angular positions

    # Opens CSV file with pre-procesed angles and uploads it to memory 
    # def initVideoAngles(self, file):
    #     self.video_angles = []
    #     with open(file, newline='') as csvfile:
    #         reader = csv.reader(csvfile, delimiter=',')
    #         for row in reader:
    #             time = float(row[0])
    #             # [left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]
    #             left_shoulder = [float(row[1]), float(row[2]) ]
    #             right_shoulder = [float(row[3]), float(row[4]) ]
    #             left_arm = [float(row[5]), float(row[6]) ]
    #             right_arm = [float(row[7]), float(row[8]) ]
    #             left_foream = [ float(row[9]), float(row[10]) ]
    #             right_foream = [ float(row[11]), float(row[12]) ]
    #             self.video_angles.append( [ time, left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ] )

    #     self.v_len = len(self.video_angles)

    # Opens CSV file with pre-procesed angles and uploads it to memory (raw version for JSON files extraction)
    def initVideoArmPoses(self, file):
        video_poses = []
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader: 
                # frame = float(row[0])
                # left_shoulder = [float(row[(5*3)+1]), float(row[(5*3)+2]) ]
                # right_shoulder = [float(row[(2*3)+1]), float(row[(2*3)+2]) ]
                # left_arm = [float(row[(6*3)+1]), float(row[(6*3)+2]) ]
                # right_arm = [float(row[(3*3)+1]), float(row[(3*3)+2]) ]
                # left_hand = [float(row[(7*3)+1]), float(row[(7*3)+2]) ]
                # right_hand = [float(row[(4*3)+1]), float(row[(4*3)+2]) ]
                # [left_shoulder, right_shoulder, left_arm, right_arm, left_hand, right_hand ]  RAW DATA FORMAT
                # video_poses.append( [ frame, left_shoulder, right_shoulder, left_arm, right_arm, left_hand, right_hand ] )
                for i in range(0, len(row)):
                    row[i] = float(row[i])
                video_poses.append(row)

        return video_poses

    # Given the time in ms, returns the vidoe arm and shoulder angles
    def getVideoArmsVectors(self, time, fps):
        # From 0 to len search 
        # for indx in range(0, self.v_len, 1):
        #     v_time = self.video_angles[indx][0]
        #     if time < v_time:
        #         # [left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]
        #         return [ self.video_angles[indx][1], self.video_angles[indx][2], self.video_angles[indx][3], self.video_angles[indx][4], self.video_angles[indx][5], self.video_angles[indx][6] ]

        # VER 2. Quicker search
        # for indx in range(self.video_angles_index, self.v_len, 1):
        #     v_time = self.video_angles[indx][0]
        #     if time <= v_time:
        #         self.video_angles_index = indx - 1
        #         if (self.video_angles_index < 0):
        #             self.video_angles_index = 0 
        #         # [left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]
        #         return [ self.video_angles[indx][1], self.video_angles[indx][2], self.video_angles[indx][3], self.video_angles[indx][4], self.video_angles[indx][5], self.video_angles[indx][6] ]

        # VER 3. raw Openpose data from JSON->CSV file
        frame = int( (fps/1000) * time )
        # left_foream = np.array( [self.video_angles[frame][7*3] - self.video_angles[frame][6*3]  ,  (self.resY - self.video_angles[frame][7*3+1]) - (self.resY - self.video_angles[frame][6*3+1]) ]  )   
        # left_arm = np.array( [ self.video_angles[frame][5*3]-self.video_angles[frame][6*3] ,    (self.resY - self.video_angles[frame][5*3+1]) - (self.resY - self.video_angles[frame][6*3+1])  ] )

        # right_foream = np.array( [self.video_angles[frame][4*3]-self.video_angles[frame][3*3]  ,  (self.resY - self.video_angles[frame][4*3+1]) - (self.resY - self.video_angles[frame][3*3+1]) ] )   
        # right_arm = np.array( [ self.video_angles[frame][2*3]-self.video_angles[frame][3*3] ,    (self.resY - self.video_angles[frame][2*3+1]) - (self.resY - self.video_angles[frame][3*3+1])  ] )

        # left_shoulder = np.array( [self.video_angles[frame][1*3]-self.video_angles[frame][5*3]  ,  (self.resY - self.video_angles[frame][1*3+1]) - (self.resY - self.video_angles[frame][5*3+1]) ] )   
        # right_shoulder = np.array( [ self.video_angles[frame][1*3]-self.video_angles[frame][2*3] ,    (self.resY - self.video_angles[frame][1*3+1]) - (self.resY - self.video_angles[frame][2*3+1])  ] )

        left_foream = np.array( [self.video_angles[frame][7*3] - self.video_angles[frame][6*3]  ,  (self.video_angles[frame][7*3+1]) - (self.video_angles[frame][6*3+1]) ]  )   
        left_arm = np.array( [ self.video_angles[frame][5*3]-self.video_angles[frame][6*3] ,    (self.video_angles[frame][5*3+1]) - (self.video_angles[frame][6*3+1])  ] )

        right_foream = np.array( [self.video_angles[frame][4*3]-self.video_angles[frame][3*3]  ,  (self.video_angles[frame][4*3+1]) - (self.video_angles[frame][3*3+1]) ] )   
        right_arm = np.array( [ self.video_angles[frame][2*3]-self.video_angles[frame][3*3] ,    (self.video_angles[frame][2*3+1]) - (self.video_angles[frame][3*3+1])  ] )

        left_shoulder = np.array( [self.video_angles[frame][1*3]-self.video_angles[frame][5*3]  ,  (self.video_angles[frame][1*3+1]) - (self.video_angles[frame][5*3+1]) ] )   
        right_shoulder = np.array( [ self.video_angles[frame][1*3]-self.video_angles[frame][2*3] ,    (self.video_angles[frame][1*3+1]) - (self.video_angles[frame][2*3+1])  ] )


        return [left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]
        
    # Compares the users's arm position with the video arms position
    # returns true if the difference is bellow the given threshold (left_arm, left_arm)
    def getArmsMatch(self, timestamp, fps, threshold):
        video_arms = self.getVideoArmsVectors(timestamp, fps)  # Gets the video arms position from the CSV file
        if video_arms is None:
            return 

        lsim_shoulder = self.calcCosineSim(self.user_arms_pos[0] , video_arms[0])
        lsim_arm = self.calcCosineSim(self.user_arms_pos[2] , video_arms[2])
        lsim_forearm = self.calcCosineSim(self.user_arms_pos[4] , video_arms[4])

        rsim_shoulder = self.calcCosineSim(self.user_arms_pos[1] , video_arms[1])
        rsim_arm = self.calcCosineSim(self.user_arms_pos[3] , video_arms[3])
        rsim_forearm = self.calcCosineSim(self.user_arms_pos[5] , video_arms[5])

        left = False
        if (lsim_shoulder > threshold) and (lsim_arm > threshold) and (lsim_forearm > threshold):
            left = True
        right = False
        if (rsim_shoulder > threshold) and (rsim_arm > threshold) and (rsim_forearm > threshold):
            right = True

        # print (str(left) + " , " + str(right))   # DEBUG ONLY
        # print ( str((lsim_shoulder+lsim_arm+lsim_forearm)/3.0), str((rsim_shoulder+rsim_arm+rsim_forearm)/3.0) )
        return [(lsim_shoulder+lsim_arm+lsim_forearm)/3.0, (rsim_shoulder+rsim_arm+rsim_forearm)/3.0]
        

    # Draws if hit were OK or NOT over the users' head
    def drawHit(self, img, event, poses):
        font = cv2.FONT_HERSHEY_SIMPLEX  # font
        org = (50, 50)  # org
        # thickness = 2  # Line thickness of 2 px

        for i, pose in enumerate(poses):
            chest = ( int(pose[1][0]), int(pose[1][1] - self.SCORE_POS )   )  # Head pos
            fontScale = 1
            thickness = 2 

            # Using cv2.putText() method
            if event[1] == True:
                img = cv2.putText(img, " OK ", chest, font, fontScale, (0, 255, 0), thickness, cv2.LINE_AA)
            else:
                img = cv2.putText(img, " X ", chest, font, fontScale, (0, 0, 255), thickness, cv2.LINE_AA)
            return img

            break  # Do it just for a single user


    # Draws the sensei arms over the users arms 
    def drawSenseiArms(self, img, poses, matches, timestamp, fps, threshold):
        # SLOW VERSION 
        # frame = int( (fps/1000) * timestamp.value )        
        # left_wrist = np.asarray([ self.video_angles[frame][7*3],  self.video_angles[frame][7*3+1] ])
        # left_elbow = np.asarray([ self.video_angles[frame][6*3],  self.video_angles[frame][6*3+1] ])
        # left_shoulder = np.asarray([ self.video_angles[frame][5*3],  self.video_angles[frame][5*3+1] ])

        # right_wrist = np.asarray([ self.video_angles[frame][4*3],  self.video_angles[frame][4*3+1] ])
        # right_elbow = np.asarray([ self.video_angles[frame][3*3],  self.video_angles[frame][3*3+1] ])
        # right_shoulder = np.asarray([ self.video_angles[frame][2*3],  self.video_angles[frame][2*3+1] ])

        # color = (0, 255, 0); 
        # if matches[0] < threshold:
        #     color = (0, 0, 255) 
        # for i, pose in enumerate(poses):
        #     sensei_l_elbow = np.asarray( [pose[5][0],pose[5][1]] ) + (left_elbow - left_shoulder) 
        #     sensei_r_elbow = np.asarray( [pose[2][0],pose[2][1]] ) + (right_elbow - right_shoulder)

        #     sensei_l_wrist = sensei_l_elbow + (left_wrist - left_elbow) 
        #     sensei_r_wrist = sensei_r_elbow + (right_wrist - right_elbow)

        #     img = cv2.line(img, ( int(pose[5][0]),int(pose[5][1])) , (int(sensei_l_elbow[0]),int(sensei_l_elbow[1]))  , color, 5)
        #     img = cv2.line(img, ( int(pose[2][0]),int(pose[2][1])) , (int(sensei_r_elbow[0]),int(sensei_r_elbow[1]))  , color, 5)

        #     img = cv2.line(img, ( int( sensei_l_elbow[0] ),int( sensei_l_elbow[1] )) , (int(sensei_l_wrist[0]),int(sensei_l_wrist[1]))  , color, 5)
        #     img = cv2.line(img, ( int( sensei_r_elbow[0] ),int( sensei_r_elbow[1] )) , (int(sensei_r_wrist[0]),int(sensei_r_wrist[1]))  , color, 5)

        #     break # only do it for the first user

        # "FAST" VERSION
        # print (fps, timestamp.value , int( (fps/1000) * timestamp.value ))
        frame = int( (fps/1000) * timestamp )     
     
        left_wrist = [self.video_angles[frame][7*3],  self.video_angles[frame][7*3+1] ]
        left_elbow = [self.video_angles[frame][6*3],  self.video_angles[frame][6*3+1] ]
        left_shoulder = [ self.video_angles[frame][5*3],  self.video_angles[frame][5*3+1] ]

        right_wrist = [ self.video_angles[frame][4*3],  self.video_angles[frame][4*3+1] ]
        right_elbow = [ self.video_angles[frame][3*3],  self.video_angles[frame][3*3+1] ]
        right_shoulder = [ self.video_angles[frame][2*3],  self.video_angles[frame][2*3+1] ]

        color = (0, 255, 0); 
        if matches[0] < threshold:
            color = (0, 0, 255)
        for i, pose in enumerate(poses):

            sensei_l_elbow = [pose[5][0] + (left_elbow[0]-left_shoulder[0]) ,pose[5][1] + (left_elbow[1]- left_shoulder[1]) ]  
            sensei_r_elbow = [pose[2][0] + (right_elbow[0]-right_shoulder[0]) ,pose[2][1] + (right_elbow[1]-right_shoulder[1])  ]      

            sensei_l_wrist = [ sensei_l_elbow[0] + (left_wrist[0] - left_elbow[0]) , sensei_l_elbow[1] + (left_wrist[1] - left_elbow[1]) ]
            sensei_r_wrist = [ sensei_r_elbow[0] +  (right_wrist[0] - right_elbow[0]), sensei_r_elbow[1] + (right_wrist[1] - right_elbow[1]) ]

            img = cv2.line(img, ( int(pose[5][0]),int(pose[5][1])) , (int(sensei_l_elbow[0]),int(sensei_l_elbow[1]))  , color, 5)
            img = cv2.line(img, ( int(pose[2][0]),int(pose[2][1])) , (int(sensei_r_elbow[0]),int(sensei_r_elbow[1]))  , color, 5)

            img = cv2.line(img, ( int( sensei_l_elbow[0] ),int( sensei_l_elbow[1] )) , (int(sensei_l_wrist[0]),int(sensei_l_wrist[1]))  , color, 5)
            img = cv2.line(img, ( int( sensei_r_elbow[0] ),int( sensei_r_elbow[1] )) , (int(sensei_r_wrist[0]),int(sensei_r_wrist[1]))  , color, 5)

            break # only do it for the first user


        
        return img

    # Draws the OpenPose person index over the users' head
    # def drawPersonNum(self, img, poses):
    #     font = cv2.FONT_HERSHEY_SIMPLEX  # font
    #     org = (50, 50)  # org
    #     fontScale = 1  # fontScale
    #     thickness = 2  # Line thickness of 2 px

    #     for i, pose in enumerate(poses):
    #         chest = ( int(pose[1][0]), int(pose[1][1] - self.INDEX_POS )   )  # Head pos
    #         img = cv2.putText(img, str(i), chest, font, fontScale, (255, 0, 0), thickness, cv2.LINE_AA)
    #     return img

    # Gets a gradient between white and green
    # def whiteGreenGradient(self, match):
    #     match = (match*255)/1.0
    #     if match < 0: match = 0
    #     if match > 255: match = 255
    #     # r = 255-match;  g = r; b = 255   # Gradient for blue
    #     r = 255-match;  g = 120; b = r     # Gradient for red
    #     return (b,g,r)

    # Draws the skeleton of the given pose in the given image  (ONLY ARMS are DRAWN) 
    def drawSkeleton(self, img, poses, matches, threshold):
        for i, pose in enumerate(poses): 
            if matches is None:
                return img
        
            # LEFT ARM
            # color = self.whiteGreenGradient(matches[0])
            # First check if the left arm was detected
            if ( (pose[7][0] + pose[7][1] != 0) and (pose[6][0] + pose[6][1] !=0) and (pose[5][0] + pose[5][1] !=0) and (pose[1][0] + pose[1][1] !=0) ):
                color = (0, 255, 0); 
                if matches[0] < threshold:
                    color = (0, 0, 255)
                img = cv2.line(img, (int(pose[7][0]),int(pose[7][1])) , (int(pose[6][0]),int(pose[6][1]))  , color, 5)
                img = cv2.line(img, (int(pose[6][0]),int(pose[6][1])) , (int(pose[5][0]),int(pose[5][1]))  , color, 5)
                img = cv2.line(img, (int(pose[5][0]),int(pose[5][1])) , (int(pose[1][0]),int(pose[1][1]))  , color, 5)
            # RIGHT ARM
            # color = self.whiteGreenGradient(matches[1])
            # Check if the right arm was detected
            if ( (pose[2][0] + pose[2][1] != 0) and (pose[3][0] + pose[3][1] !=0) and (pose[4][0] + pose[4][1] !=0) and (pose[1][0] + pose[1][1] !=0) ):
                color = (0, 255, 0); 
                if matches[1] < threshold:
                    color = (0, 0, 255)
                img = cv2.line(img, (int(pose[1][0]),int(pose[1][1])) , (int(pose[2][0]),int(pose[2][1]))  , color, 5)
                img = cv2.line(img, (int(pose[2][0]),int(pose[2][1])) , (int(pose[3][0]),int(pose[3][1]))  , color, 5)
                img = cv2.line(img, (int(pose[3][0]),int(pose[3][1])) , (int(pose[4][0]),int(pose[4][1]))  , color, 5)
            break # Do it only for the first found person
    
        return img

    # Gets the vectors of the shoulder, arm and forearm
    def getArmsVectors(self, pose):
        # left_foream = np.array(  [ pose[7][0] - pose[6][0] , (self.resY - pose[7][1]) - (self.resY - pose[6][1])  ] )
        # left_arm = np.array(  [ pose[5][0] - pose[6][0] ,    (self.resY - pose[5][1]) - (self.resY - pose[6][1])  ] )
        
        # right_foream = np.array(  [ pose[4][0] - pose[3][0] , (self.resY - pose[4][1]) - (self.resY - pose[3][1] ) ] )
        # right_arm = np.array(  [ pose[2][0] - pose[3][0] ,    (self.resY - pose[2][1]) - (self.resY - pose[3][1] ) ] )
        
        # left_shoulder = np.array(  [ pose[1][0] - pose[5][0] , (self.resY - pose[1][1]) - (self.resY - pose[5][1])  ] )
        # right_shoulder = np.array(  [ pose[1][0] - pose[2][0] , (self.resY - pose[1][1]) - (self.resY - pose[2][1])  ] )

        left_foream = np.array(  [ pose[7][0] - pose[6][0] , (pose[7][1]) - (pose[6][1])  ] )
        left_arm = np.array(  [ pose[5][0] - pose[6][0] ,    (pose[5][1]) - (pose[6][1])  ] )
        
        right_foream = np.array(  [ pose[4][0] - pose[3][0] , (pose[4][1]) - (pose[3][1] ) ] )
        right_arm = np.array(  [ pose[2][0] - pose[3][0] ,    (pose[2][1]) - (pose[3][1] ) ] )
        
        left_shoulder = np.array(  [ pose[1][0] - pose[5][0] , (pose[1][1]) - (pose[5][1])  ] )
        right_shoulder = np.array(  [ pose[1][0] - pose[2][0] , (pose[1][1]) - (pose[2][1])  ] )
        
        return [left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]

    # Calcuates the angular velocity between the arm/forearm and forearm/shoulder
    def logArmsVel(self, poses):
        user_arms = []
        for i, pose in enumerate(poses): 

            self.user_arms_pos = self.getArmsVectors(pose)

            # calculate the arms and shoulder angles
            # [left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]
            left_sh_angle =  self.calcVectorAngle(self.user_arms_pos[0], self.user_arms_pos[2])  # left_shoulder and left_arm
            right_sh_angle = self.calcVectorAngle(self.user_arms_pos[1], self.user_arms_pos[3])  # right_shoulder and right_arm
            left_arm_angle = self.calcVectorAngle(self.user_arms_pos[2], self.user_arms_pos[4])  # left_arm and left_forearm
            right_arm_angle = self.calcVectorAngle(self.user_arms_pos[3], self.user_arms_pos[5])  # right_arm and right_forearm

            # Calculate the angular velocity
            now_sec = time.time_ns() / 1000000000   # time in SECONDS (for velocity)
            dt = now_sec - self.prev_time 
            left_sh_vel  = (self.prev_arms_angle[0] - left_sh_angle) / dt   # left shoulder vel
            right_sh_vel = (self.prev_arms_angle[1] - right_sh_angle) / dt   # right shoulder vel
            left_arm_vel  = (self.prev_arms_angle[2] - left_arm_angle) / dt   # left arm vel  
            right_arm_vel = (self.prev_arms_angle[3] - right_arm_angle) / dt   # right arm vel

            # saving current angle for next loop
            # [left_shoulder_angle, right_shoulder_angle, left_arm_angle, right_arm_angle]
            self.prev_arms_angle[0] = left_sh_angle;  self.prev_arms_angle[1] = right_sh_angle; 
            self.prev_arms_angle[2] = left_arm_angle; self.prev_arms_angle[3] = right_arm_angle; 
            self.prev_time = now_sec

            now = int(time.time_ns() / 1000000)  # log time in ms
            user_arms.append( (now, left_sh_angle, right_sh_angle, left_arm_angle, right_arm_angle, left_sh_vel, right_sh_vel, left_arm_vel, right_arm_vel) )  # 0 max 1 min
            break   # make this only for the first pose (single user)

        self.armsLogs.append(user_arms)

    # Calculates the audio volume depeding on how high the user has his hands 
    def logArmsHeight(self, poses):        
        for i, pose in enumerate(poses): 

            left_wrist = np.array(  [ pose[5][0] - pose[7][0] , (pose[5][1]) - (pose[7][1])  ] )
            right_wrist = np.array(  [ pose[2][0] - pose[4][0] , (pose[2][1]) - (pose[4][1] ) ] )

            left_shoulder = np.array(  [ pose[1][0] - pose[5][0] , (pose[1][1]) - (pose[5][1])  ] )
            right_shoulder = np.array(  [ pose[1][0] - pose[2][0] , (pose[1][1]) - (pose[2][1])  ] )

            # calculate the wrist and shoulder angles            
            left_arm_angle = self.rawVectorAngle(np.array( [0.0 , 1.0] ), left_wrist ) # raw dot product vector angle
            right_arm_angle = self.rawVectorAngle(np.array( [0.0 , 1.0] ), right_wrist)  # raw dot product vector angle
                        
            # print (left_arm_angle, right_arm_angle)  # DEBUG
            # print (self.map_range( left_arm_angle, -1, 1, 0, 127), self.map_range( right_arm_angle, -1, 1, 0, 127) )  # mapped result #DEBUG

            # save raw dotproduct angle and time in a log 
            now = int(time.time_ns() / 1000000)
            self.arms_hlog.append([ now, self.map_range( left_arm_angle, -1, 1, 0, 127), self.map_range( right_arm_angle, -1, 1, 0, 127) ])
            # print (self.arms_hlog[-1])
            # self.updateLastMaxHeight()
            break   # make this only for the first pose (single user)


    # Updates the last value 
    def updateLastMaxHeight(self):
        UPDATE_LENGHT = 1000  # 1 sec
        
        N = len(self.arms_hlog)
        for indx in range(N,0,-1):
            pass
            
    # calculates the angle between two given vectors
    def calcVectorAngle(self, vector_1, vector_2):
        unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
        unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
        dot_product = np.dot(unit_vector_1, unit_vector_2)
        angle = np.arccos(dot_product)
        degs = (180.0/math.pi) * angle

        return degs


    # calculates the angle between two given vectors
    # returns the raw results from the dot product, which is always between -1 to 1
    def rawVectorAngle(self, vector_1, vector_2):
        unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
        unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
        dot_product = np.dot(unit_vector_1, unit_vector_2)

        return dot_product

    def map_range(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    # Calculates the cosine similarity between two given vectors
    def calcCosineSim(self, vector_1, vector_2):
        cdot = np.dot(vector_1, vector_2)
        vec_norm1 = np.linalg.norm(vector_1)
        vec_norm2 = np.linalg.norm(vector_2)
        return (cdot / (vec_norm1 * vec_norm2))

    # Save the arms and shoulders position on CSV Format
    def logOnDisk(self):
        with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            wr.writerow(['Index', 'Time(epoch ms)', 'Left_Sh_Angle(deg)', 'Right_Sh_Angle(deg)', 'Left_Arm_Angle(deg)', 'Right_Arm_Angle(deg)', 'Left_Sh_Vel(deg/s)', 'Right_Sh_Vel(deg/s)', 'Left_Arm_Vel(deg/s)', 'Right_Arm_Vel(deg/s)'])
            for i, line in enumerate(self.armsLogs):
                wr.writerow([i, line[0][0], line[0][1], line[0][2], line[0][3], line[0][4], line[0][5], line[0][6], line[0][7], line[0][8] ])


                    