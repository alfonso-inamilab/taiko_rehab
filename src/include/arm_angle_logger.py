import time
import cv2
import math
import csv
import pandas as pd
import numpy as np
from pprint import pprint
from array import array
from threading import Thread

# Class that calculates the angle between the forearm and arm 
# and saves all the data in a log
class ArmAngleLog:

    def __init__(self, resX, resY, video_angles_file, log_file):
        self.log_file = log_file
        self.video_angles = None
        self.v_len = 0
        self.initVideoAngles(video_angles_file)
        self.resX = resX
        self.resY = resY
        self.INDEX_POS = 100
        self.SCORE_POS = 60
        self.armsLogs = []
        self.prev_time = 0

        self.user_arms_pos = [0.0, 0.0, 0.0, 0.0]   # current arm angular positions
        self.user_arms_vel = [0.0, 0.0, 0.0, 0.0]   # current arm angular velocities
        self.prev_arms_pos = [0.0, 0.0, 0.0, 0.0]   # last cycle arms angular positions
        self.red =   (0,0,255)  #B,G,R colors to draw the Skeleton
        self.green = (0,255,0)  #B,G,R colors to draw the Skeleton

    # Opens CSV file with pre-procesed angles and uploads it to memory 
    def initVideoAngles(self, file):
        self.video_angles = []
        with open(file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                time = float(row[0])
                # [left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]
                left_shoulder = [float(row[1]), float(row[2]) ]
                right_shoulder = [float(row[3]), float(row[4]) ]
                left_arm = [float(row[5]), float(row[6]) ]
                right_arm = [float(row[7]), float(row[8]) ]
                left_foream = [ float(row[9]), float(row[10]) ]
                right_foream = [ float(row[11]), float(row[12]) ]
                self.video_angles.append( [ time, left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ] )

        self.v_len = len(self.video_angles)

    # Given the time in ms, returns the vidoe arm and shoulder angles
    def getCurrentAngles(self, time):
        # From 0 to len search 
        for indx in range(0, self.v_len, 1):
            v_time = self.video_angles[indx][0]
            if time < v_time:
                # [left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]
                return [ self.video_angles[indx][1], self.video_angles[indx][2], self.video_angles[indx][3], self.video_angles[indx][4], self.video_angles[indx][5], self.video_angles[indx][6] ]

    # Compares the users's arm position with the video arms position
    # returns true if the difference is bellow the given threshold (left_arm, left_arm)
    def getArmsMatch(self, timestamp, threshold):
        video_arms = self.getCurrentAngles(timestamp.value)  # Gets the video arms position from the CSV file
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

        print (str(left) + " , " + str(right))   # DEBUG ONLY
        return [left, right]
        

    # Draws if hit were OK or NOT over the users' head
    def drawHit(self, img, events, poses):
        font = cv2.FONT_HERSHEY_SIMPLEX  # font
        org = (50, 50)  # org
        # thickness = 2  # Line thickness of 2 px

        for i, pose in enumerate(poses):
            chest = ( int(pose[1][0]), int(pose[1][1] - self.SCORE_POS )   )  # Head pos
            fontScale = 1
            thickness = 2 

            # Using cv2.putText() method
            if events[i][4] == 1:
                img = cv2.putText(img, " OK ", chest, font, fontScale, (0, 255, 0), thickness, cv2.LINE_AA)
            else:
                img = cv2.putText(img, " X ", chest, font, fontScale, (0, 0, 255), thickness, cv2.LINE_AA)
            return img

    # Draws the OpenPose person index over the users' head
    def drawPersonNum(self, img, poses):
        font = cv2.FONT_HERSHEY_SIMPLEX  # font
        org = (50, 50)  # org
        fontScale = 1  # fontScale
        thickness = 2  # Line thickness of 2 px

        for i, pose in enumerate(poses):
            chest = ( int(pose[1][0]), int(pose[1][1] - self.INDEX_POS )   )  # Head pos
            img = cv2.putText(img, str(i), chest, font, fontScale, (255, 0, 0), thickness, cv2.LINE_AA)
        return img

    # Draws the skeleton of the given pose in the given image  (ONLY ARMS are DRAWN) 
    def drawSkeleton(self, img, poses, matches):

        return img

    # Gets the vectors of the shoulder, arm and forearm
    def getArmsVectors(self, pose):
        left_foream = np.array(  [ pose[7][0] - pose[6][0] , (self.resY - pose[7][1]) - (self.resY - pose[6][1])  ] )
        left_arm = np.array(  [ pose[5][0] - pose[6][0] ,    (self.resY - pose[5][1]) - (self.resY - pose[6][1])  ] )
        
        right_foream = np.array(  [ pose[4][0] - pose[3][0] , (self.resY - pose[4][1]) - (self.resY - pose[3][1] ) ] )
        right_arm = np.array(  [ pose[2][0] - pose[3][0] ,    (self.resY - pose[2][1]) - (self.resY - pose[3][1] ) ] )
        
        left_shoulder = np.array(  [ pose[1][0] - pose[5][0] , (self.resY - pose[1][1]) - (self.resY - pose[5][1])  ] )
        right_shoulder = np.array(  [ pose[1][0] - pose[2][0] , (self.resY - pose[1][1]) - (self.resY - pose[2][1])  ] )
        
        return [left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]

    # Calcuates the angular velocity between the arm/forearm and forearm/shoulder
    def calcArmVel(self, poses):
        user_arms = []
        for i, pose in enumerate(poses): 

            self.user_arms_pos = self.getArmsVectors(pose)

            now_sec =int ( time.time_ns() / 100000000)
            dt = now_sec - self.prev_time 
            left_arm_vel  = (self.prev_arms_pos[0] - self.user_arms_pos[0]) / dt   # left arm vel  
            right_arm_vel = (self.prev_arms_pos[1] - self.user_arms_pos[1]) / dt   # right arm vel

            left_sh_vel  = (self.prev_arms_pos[2] - self.user_arms_pos[2]) / dt   # left shoulder vel
            right_sh_vel = (self.prev_arms_pos[3] - self.user_arms_pos[3]) / dt   # right shoulder vel

            self.prev_arms_pos = self.user_arms_pos
            self.prev_time = now_sec

            now = int(time.time() * 1000)
            user_arms.append( (now, left_arm_vel, right_arm_vel, left_sh_vel, right_sh_vel) )  # 0 max 1 min
            break   # make this only for the first pose (single user)

        self.armsLogs.append(user_arms)

    
    # calculates the angle between two given vectors
    def calcVectorAngle(self, vector_1, vector_2):
        unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
        unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
        dot_product = np.dot(unit_vector_1, unit_vector_2)
        angle = np.arccos(dot_product)
        degs = (180.0/math.pi) * angle

        return degs

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

            wr.writerow(['User_ID', 'Time_Lapse(ms)', 'Time(epoch)', 'Left_Height(Norm)', 'Right_Height(Norm)', 'Left_Height(Raw)', 'Right_Height(Raw)'])
            first_event = 0
            for i, line in enumerate(self.armsLogs):
                if i ==0:
                    first_event = line[0][0]
                wr.writerow(['0', line[0][0]-first_event, line[0][0], line[0][1], line[0][2], line[0][3], line[0][4] ])

            del self.armsLogs[:]   #clean logged wrist positions

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
                    