import vlc

from multiprocessing import Process
from multiprocessing import Event, Value


# Starts the player and syncs the midi player with a synched flag
def videoPlayLoop(videopath, start_event, video_play, timestamp):

        player = None
        player = vlc.MediaPlayer(videopath)
        # player.video_set_scale(video_scale)    

        player.play()
        print ("player ON")
        
        while (video_play.value == True):
            # timestamp.value = player.get_time()
            if player.get_time() > 0:
                start_event.set()
                # return
        return

class VideoDisplay():

    def __init__(self, videopath, timestamp, deque_size, start_event, video_scale=1.0 ):
        self.fps = 0
        self.length = 0
        

        self.video_play = Value('b', False)
        self.timestamp = Value('l', False)
        self.videoPlayThread = Process(name="p_midi", target=videoPlayLoop, args=( videopath, start_event, self.video_play, self.timestamp )  ) 
        self.videoPlayThread.daemon = True
        # self.startThread = Thread(target=self.startingLoop, args=(start_event,))
        # self.startThread.daemon = True

    # Starts the video process
    def start(self):
        # Start background frame grabbing   
        self.video_play.value = True
        self.videoPlayThread.start()        

    # Stops the video process
    def stop(self):
        self.video_play.value = False
        # self.videoPlayThread.stop()

    # def getHMSTime(self):
    #     millis = self.get_timestamp()

    #     millis = int(millis)
    #     seconds=(millis/1000)%60
    #     frac = int ( (seconds % 1) * 1000) 
    #     seconds = int(seconds)
    #     minutes=(millis/(1000*60))%60
    #     minutes = int(minutes)
    #     hours=(millis/(1000*60*60))%24

    #     return ("%02d:%02d:%02d.%03d" % (hours, minutes, seconds, frac))

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
            
                