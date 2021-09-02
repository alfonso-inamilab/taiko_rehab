import cv2
import numpy as np
import pyrealsense2 as rs
from threading import Thread
from collections import deque

class camThread():

    def __init__(self, cameraID, deque_size):
        # self.resX = resX; self.resY = resY
        self.cap = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)

        self.deque = deque(maxlen=deque_size)   # Initialize deque used to store frames read from the stream
        self.get_frame_thread = Thread(target=self.get_frame, args=())
        self.get_frame_thread.daemon = True

        # Check if the UV camera opened successfully
        if self.cap.isOpened() == False:
            print("Error opening video stream or file")

        #change webcam resolution
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resX)  
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resY) 

    def start(self):
        # Start background frame grabbing
        self.get_frame_thread.start() 

    def stop(self):
        self.cap.release()

    def get_frame(self):
        while True:            
            if self.cap.isOpened():
                # Read next frame from stream and insert into deque
                ret, image = self.cap.read()  #uv camera
                if ret:
                    self.deque.append(image)
                
    def get_video_frame(self):
        if len(self.deque) > 0:
            return self.deque[-1]
        else:
            # print ('no frames ;(')
            return None 
