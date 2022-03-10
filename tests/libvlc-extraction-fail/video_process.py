# SAMPLES TAKEN FROM 
# USE PIL TO OPEN LIBVLC CTYPES BUFFER

# TRANSFORM PIL IMAGE TO OPENCV FORMAT (
# https://qiita.com/derodero24/items/f22c22b22451609908ee



import vlc
import ctypes
import time
import sys
import os
import csv
import numpy as np
import cv2

from PIL import Image

VIDEOWIDTH = 1280
VIDEOHEIGHT = 720

from globals import OP_PY_DEMO_PATH
from globals import OP_MODELS_PATH
sys.path.append(OP_PY_DEMO_PATH + '/../../python/openpose/Release')
os.environ['PATH']  = os.environ['PATH'] + ';' + OP_PY_DEMO_PATH + '/../../x64/Release;' +  OP_PY_DEMO_PATH + '/../../bin;'
import pyopenpose as op

# vlc.CallbackDecorators.VideoLockCb is incorrect
CorrectVideoLockCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))


@CorrectVideoLockCb
def _lockcb(opaque, planes):
    # print("lock", file=sys.stderr)
    vp = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value

    planes[0] = vp.get_buffer_pt()

# MY MODIFIED FUNCTION TO USE OPENCV INSTEAD 
# process all the frames, not just every 24 frames
@vlc.CallbackDecorators.VideoDisplayCb
def _display(opaque, picture):
    vp = ctypes.cast(opaque, ctypes.POINTER(ctypes.py_object)).contents.value

    img = Image.frombuffer("RGBA", (VIDEOWIDTH, VIDEOHEIGHT), vp.get_buffer(), "raw", "BGRA", 0, 1)
    new_image = np.array(img, dtype=np.uint8)
    new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    
    # cv2.imwrite('img{}.png'.format(framenr), new_image)
    # cv2.imshow("pil sample", new_image)
    # key = cv2.waitKey(1)

    vp.process_frame(new_image)

class VideoProcess():
    
    def __init__(self, video_path, save_csv_path):
        self.pl = vlc.MediaPlayer(video_path)

         # INIT OpenCV block
        params = dict()
        params["model_folder"] = OP_MODELS_PATH
        params["number_people_max"] = 1 #MAX_NUM_PEOPLE

        # Init OpenPose python wrapper
        self.opWrapper = op.WrapperPython()
        self.opWrapper.configure(params)
        self.opWrapper.start()
        self.datum = op.Datum()
        # INIT OpenCV block

        # size in bytes when RV32
        size = VIDEOWIDTH * VIDEOHEIGHT * 4
        # allocate buffer
        self.buf = (ctypes.c_ubyte * size)()
        # get pointer to buffer
        self.buf_p = ctypes.cast(self.buf, ctypes.c_void_p)

        # global frame (or actually displayed frame) counter
        self.framenr = 0
        self.vtime = 0

        self.resY = VIDEOHEIGHT
        self.resX = VIDEOWIDTH

        # Open csv file 
        self.csvfile = open(save_csv_path, 'w', newline='') 
        self.writer = csv.writer(self.csvfile)

    def get_buffer_pt(self):
        return self.buf_p

    def get_buffer(self):
        return self.buf

    def get_player(self):
        return self.pl

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

    def process_frame(self, frame):
        timestamp = vp.get_player().get_time()

        self.datum.cvInputData = frame
        self.opWrapper.emplaceAndPop(op.VectorDatum([self.datum])) 
        
        #  Get the vectors of the arms and shoulders
        if self.datum.poseKeypoints is not None:
            vectors = self.getArmsVectors(self.datum.poseKeypoints)
            img_out = self.datum.cvOutputData
            cv2.imshow("Taiko Rehab", img_out)  # open pose img
            # key = cv2.waitKey(1)
            # if key == 27  or key & 0xFF == ord('q'):   # ESC or q to exit
            #     break

            print(timestamp)
            print(vectors)
            # [timestamp, left_shoulder, right_shoulder, left_arm, right_arm, left_foream, right_foream ]
            self.writer.writerow( [timestamp, vectors[0][0], vectors[0][1],
                                            vectors[1][0], vectors[1][1],
                                            vectors[2][0], vectors[2][1],
                                            vectors[3][0], vectors[3][1],
                                            vectors[4][0], vectors[4][1],
                                            vectors[5][0], vectors[5][1] ] )
        


    def close(self):
        self.csvfile.close()
        cv2.destroyAllWindows()


vp = VideoProcess('C:/rehab/src/taiko_rehab/src/samples/sample1.mp4', 'C:/rehab/src/taiko_rehab/src/samples/pinchixxx.csv')

vp_obj = ctypes.py_object(vp)
vp_ptr = ctypes.byref(vp_obj)

vlc.libvlc_video_set_callbacks(vp.pl, _lockcb, None, _display, vp_ptr)
vp.pl.video_set_format("RV32", VIDEOWIDTH, VIDEOHEIGHT, VIDEOWIDTH * 4)


vp.pl.play()
while True:
    pass

vp.close()
