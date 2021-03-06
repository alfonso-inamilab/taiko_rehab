import time
import cv2
import math
import csv
import pandas as pd
import numpy as np
from pprint import pprint
from threading import Thread

class OPWristPos:

    def __init__(self, resX, resY, log_file):
        self.log_file = log_file
        self.resX = resX
        self.resY = resY
        self.INDEX_POS = 100
        self.SCORE_POS = 60
        self.wristLogs = []

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
            if events[i][4] == 'HIT':
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


    # Returns the users' wrist elevation and logs their movements into memory
    def logWristElevation(self, poses):
        ret_pos = []  # Left and Right wrist elevation of each person
        for i, pose in enumerate(poses): 
            # Get the user's wrist height 
            left_height = pose[7][1]   
            right_height = pose[4][1]   
        
            # Normalize the position accordingly to the image resolution
            left_norm_h = left_height / self.resY
            right_norm_h = right_height / self.resY

            now = int(time.time() * 1000)
            ret_pos.append( (now, left_norm_h, right_norm_h, left_height, right_height) )  # 0 max 1 min
        
        self.wristLogs.append(ret_pos)
        return ret_pos

    # Save the wrist position on CSV Format
    def logOnDisk(self):
        with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            wr.writerow(['User_ID', 'Time_Lapse(ms)', 'Time(epoch)', 'Left_Height(Norm)', 'Right_Height(Norm)', 'Left_Height(Raw)', 'Right_Height(Raw)'])
            first_event = 0
            for i, line in enumerate(self.wristLogs):
                if i ==0:
                    first_event = line[0][0]
                wr.writerow(['0', line[0][0]-first_event, line[0][0], line[0][1], line[0][2], line[0][3], line[0][4] ])

            del self.wristLogs[:]   #clean logged wrist positions

    # Joins all the CSV log files into a single file (Using Pandas)
    def joinCsvLogs(self, force_log_file, midi_log_file , wrist_log_file, full_log_file ):
        # Open every CSV in a independent dataframe
        force = pd.read_csv(force_log_file, index_col=None, header=0)
        wrist = pd.read_csv(wrist_log_file, index_col=None, header=0)
        midi = pd.read_csv(midi_log_file, index_col=None, header=0)
        # Merge force and wrist data frames
        force_wrist = pd.concat([force,wrist])
        force_wrist = force_wrist.sort_values('Time(epoch)')
        # Merge force wrist and midi dataframes
        force_wrist_midi =  pd.concat([force_wrist, midi])
        force_wrist_midi = force_wrist_midi.sort_values('Time(epoch)')
        force_wrist_midi = force_wrist_midi.drop('Time_Lapse(ms)',1)   # Drop Time lapse it is not needed
        force_wrist_midi.to_csv(full_log_file, index=False)   # Save on CSV file
                    