import time
import cv2
import math
import numpy as np
from threading import Thread

class OPWristPos:

    def __init__(self, resX, resY, log_file):
        self.log_file = log_file
        self.resX = resX
        self.resY = resY
        self.INDEX_POS = 100
        self.SCORE_POS = 60

    # Draws if hit were OK or NOT over the users' head
    def drawHitOK(self, img, events, poses):
        font = cv2.FONT_HERSHEY_SIMPLEX  # font
        org = (50, 50)  # org
        # thickness = 2  # Line thickness of 2 px

        for i, pose in enumerate(poses):
            chest = ( int(pose[1][0]), int(pose[1][1] - self.SCORE_POS )   )  # Head pos
            fontScale = 1
            thickness = 2 

            # Using cv2.putText() method
            if events[i][4]:
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


    # Returns the users' wrist elevation and log their movements in a csv
    def getWristElevation(self, poses):
        ret_pos = []  # Left and Right wrist elevation of each person
        for i, pose in enumerate(poses): 
            # Get the user's wrist height 
            left_height = pose[7][1]   
            right_height = pose[4][1]   
        
            # Normalize the position accordingly to the image resolution
            left_norm_h = left_height / self.resY
            right_norm_h = right_height / self.resY

            ret_pos.append( (left_norm_h, right_norm_h) )
        return ret_pos
