import time
import cv2
import math
import csv
import pandas as pd
import numpy as np
from pprint import pprint
from threading import Thread

class OPWristPos:

    def __init__(self, resX, resY):
        self.resX = resX
        self.resY = resY

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
                    