import sys
import mido
import time
from mido import MidiFile
from multiprocessing import Process
# from threading import Thread

class midiPlayer():

    def __init__(self, portname, filename):
        # self.player_thread = Thread(target=self.playing_loop, args=())
        # self.player_thread.daemon = True 
        p = Process(target=self.playing_loop, args=())
        self.play = False

        self.output = mido.open_output(portname)
        self.midifile = MidiFile(filename)
        self.p.start()

    # Plays and pause the midi player
    def play_pause(self):
        self.play = not self.play

    # Stops the thread that plays the midi file
    def stop(self):
        self.cap.release()

    # Function that handles the playing 
    def playing_loop(self):

        # with mido.open_output(portname) as output:
        try:
            t0 = time.time()
            for message in self.midifile.play():
                print(message)
                self.output.send(message)
            print('play time: {:.2f} s (expected {:.2f})'.format(
                    time.time() - t0, self.midifile.length))

        except KeyboardInterrupt:
            print()
            self.output.reset()



        # This version do not work too
        # midifile.play is a generator (https://realpython.com/introduction-to-python-generators/)
        # for message in self.midifile.play():
        #     if self.play:
        #         if message.type == 'set_tempo':
        #             print('Tempo changed to {:.1f} BPM.'.format(tempo2bpm(message.tempo)))
        #         # print(message)
        #         self.output.send(message)

        # THis version do not work
        # for msg in self.midifile:
        #     time.sleep(msg.time)
        #     print(msg.time)
        #     if not msg.is_meta:
        #         self.output.send(msg)


            
    # Returns the current time keept by the player
    def get_time(self):
        pass

    # Returns the current time of the midi player
    def get_tick(self):
        pass



# filename = sys.argv[1]
# if len(sys.argv) == 3:
#     portname = sys.argv[2]
# else:
#     portname = None

# with mido.open_output(portname) as output:
#     try:
#         midifile = MidiFile(filename)
#         t0 = time.time()
#         for message in midifile.play():
#             print(message)
#             output.send(message)
#         print('play time: {:.2f} s (expected {:.2f})'.format(
#                 time.time() - t0, midifile.length))

#     except KeyboardInterrupt:
#         print()
#         output.reset()