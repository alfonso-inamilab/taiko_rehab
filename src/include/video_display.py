import time
import numpy as np
import cv2 as cv
import wx
import wx.media


from threading import Thread
from multiprocessing import Process
from multiprocessing import Event, Value
from ffpyplayer.player import MediaPlayer

# WX Frame to display the video. It also creates an external thread to updtea the video timestamp (ms)
class VideoPanel(wx.Frame):
    def __init__(self, videopath, start_event, start_frame, fps, timestamp):
        wx.Frame.__init__(self, None, size=wx.Size(1024,720))
        self.testMedia = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER,szBackend=wx.media.MEDIABACKEND_WMP10)
        self.testMedia.Bind(wx.media.EVT_MEDIA_LOADED, self.play)
        self.testMedia.Bind(wx.media.EVT_MEDIA_FINISHED, self.quit)
        if self.testMedia.Load(videopath):
            pass
        else:
            print("Media not found")
            self.quit(None)

        self.stop_flag = Value('b', False)
        self.th = Thread(target=self.getTime, args=(start_event, start_frame, fps, timestamp, self.stop_flag ))
        self.th.daemon = True
        self.th.start()


    def play(self, event):
        self.stop_flag.value = False
        self.testMedia.Play()

    def quit(self, event):
        self.stop_flag.value = True
        self.th.join()
        self.Destroy()


    # Thread looping function to update the video timestamp
    def getTime(self, start_event, start_frame, fps, timestamp, stop_flag):

        FIRST_HIT_TIME = int((start_frame / fps) * 1000)
        
        first_hit = True
        while (stop_flag.value == False):
            timestamp.value = self.testMedia.Tell()
            
            if (timestamp.value > FIRST_HIT_TIME and first_hit == True):
                start_event.set()
                first_hit = False

# External process to create the WXFrame display the video and update the video timestamp
def videoPlayLoop(videopath, start_event, start_frame, fps, timestamp ):
    app = wx.App()
    Frame = VideoPanel(videopath, start_event, start_frame, fps, timestamp)
    Frame.Show()
    app.MainLoop()


# Class that encapsulates the VideoDisplay process and control
class VideoDisplay():

    def __init__(self, videopath, timestamp, deque_size, start_event, start_frame, video_scale=1.0):
        # Use Opencv to get the videO FPS
        tmp_video = cv.VideoCapture(videopath)
        self.fps = float(tmp_video.get(cv.CAP_PROP_FPS))
        tmp_video.release()

        self.length = 0
        self.videoPlayProc = Process(name="p_midi", target=videoPlayLoop, args=( videopath, start_event, start_frame, self.fps, timestamp )  ) 
        self.videoPlayProc.daemon = True

    # Starts the video process
    def start(self):
        # Start background frame grabbing  
        self.videoPlayProc.start()        

    # Stops the video process
    def stop(self):
        if self.videoPlayProc.is_alive():
            self.videoPlayProc.terminate()

    # Retruns the FPS obtained with OpenCV
    def get_fps(self):
        return self.fps


    
                