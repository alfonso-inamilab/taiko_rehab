import vlc
from threading import Thread
from multiprocessing import Event

class VideoDisplay():

    def __init__(self, videopath, timestamp, deque_size, start_event, video_scale=1.0 ):
        self.fps = 0
        self.length = 0
        self.player = None
        self.player = vlc.MediaPlayer(videopath)
        self.player.video_set_scale(video_scale)    

        self.startThread = Thread(target=self.startingLoop, args=(start_event,))

    # Starts the media video plaeyr
    def start(self):
        # Start background frame grabbing   
        self.startThread.start()

    # Starts the player and syncs the midi player with a synched flag
    def startingLoop(self, start_event):
        self.player.play()
        print ("player ON")
        while (True):
            if self.player.get_time() > 0:
                start_event.set()
                print ("video started")
                return
        return
            

    # Stops the media player
    def stop(self):
        self.player.stop()

    def getHMSTime(self):
        millis = self.get_timestamp()

        millis = int(millis)
        seconds=(millis/1000)%60
        frac = int ( (seconds % 1) * 1000) 
        seconds = int(seconds)
        minutes=(millis/(1000*60))%60
        minutes = int(minutes)
        hours=(millis/(1000*60*60))%24

        return ("%02d:%02d:%02d.%03d" % (hours, minutes, seconds, frac))

    def get_timestamp(self):
        if self.player is None :
            return 0
        else:
            return self.player.get_time() 

    def get_length(self):
        if self.player is None:
            return 0
        else:
            return self.player.get_length()

    def get_fps(self):
        if self.player is None:
            return 0
        else:
            return self.player.get_fps()
            
                