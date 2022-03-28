import sys
sys.coinit_flags = 2  # COINIT_APARTMENTTHREADED
import os

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

# IMPORTING GLOBAL PARAMETERS 
from include.globals import OP_PY_DEMO_PATH
from include.globals import OP_MODELS_PATH
from include.globals import CAM_OPCV_ID
from include.globals import MAX_TXT_FRAMES
from include.globals import MIDI_MAX_PAST
from include.globals import MIDI_MAX_FUTURE
from include.globals import MIDI_PLAY_GOOD_HITS
from include.globals import MIDI_PLAY_ALL_HITS
from include.globals import MIDI_PLAY_MIDIFILE_NOTES
from include.globals import DRAW_SENSEI_ARMS
from include.globals import DRAW_HITS
from include.globals import JOY_BUFF_SIZE
from include.globals import JOY_CNX_NUMBER
from include.globals import MIDI_MIN_ARM_VOL
from include.globals import MIDI_MAX_ARM_VOL
from include.globals import MIDI_SYNTH_LATENCY


# IMPORT CLASS FOR THE TAIKO MAIN PROGRAM CONTROL
from taiko_control import taikoControl

class taikoGUI():

    def __init__(self,taiko_ctrl):
        # Pre process section GUI objects
        self.txt01 = None
        self.txt02 = None
        # Trainning section GUI objects
        self.txt1_1 = None
        self.txt1_2 = None
        self.txt1_3 = None
        self.txt1_22 = None
        # Option section GUI objects
        self.txt1 = None
        self.txt2 = None
        self.txt4 = None
        self.txt5 = None
        self.txt10 = None   # midi max past reaction value 
        self.txt11 = None   # midi max future reaction value
        self.txt12 = None   # joystick log event buffer size
        self.txt13 = None  # joystick cnx number
        self.txt14 = None   #midi min arm volume value
        self.txt15 = None   # midi max arm volume value
        self.txt16 = None   # midi synth latency value
        self.midi_play_file_notes = None
        self.midi_play_good_hits = None
        self.midi_play_all_hits = None
        self.draw_sensei_arms = None
        self.draw_hits = None

        self.combo3 = None
        self.instructor = None
        self.visual_feedback = None
        self.user_camera = None
        # Class to control the other clases
        self.taiko_ctrl = taiko_ctrl

    # save the config file direclty re-writing the global.py file
    def save(self):

        if self.checkBeforeSafe() == False:
            return 

        with open('include/globals.py', 'w') as f:
            f.write("# OPENCV GLOBAL VARIABLES \n")
            f.write("OP_MODELS_PATH = \""  + self.txt1.get().replace('\\','\\\\') +  "\" # OpenPose models folder \n")
            f.write("OP_PY_DEMO_PATH = \""  + self.txt2.get().replace('\\','\\\\') +  "\" # OpenPose demo folder \n")
            f.write("CAM_OPCV_ID = " + self.combo3.get() +   " # Open CV camera ID \n" )
            f.write("MAX_TXT_FRAMES = " + self.txt4.get()  + " # Number of frames the text wrist will be in the screen \n")

            f.write("\n# PROGRAM GLOBAL VARIABLES \n") 
            f.write("DRAW_SENSEI_ARMS = " + str(self.draw_sensei_arms.get())  + " \n")
            f.write("DRAW_HITS = " + str(self.draw_hits.get())  + " \n")

            f.write("\n# MIDI CONTROL VARIABLES \n") 
            f.write("MIDI_MAX_PAST = "  + self.txt10.get()  + " \n")
            f.write("MIDI_MAX_FUTURE = " + self.txt11.get()  + " \n")
            f.write("MIDI_PLAY_GOOD_HITS = " + str(self.midi_play_good_hits.get())  + " \n")
            f.write("MIDI_PLAY_ALL_HITS = " + str(self.midi_play_all_hits.get())  + " \n")
            f.write("MIDI_PLAY_MIDIFILE_NOTES = " + str(self.midi_play_file_notes.get())  + " \n")
            f.write("MIDI_MAX_ARM_VOL = "  + self.txt14.get()  + " \n")
            f.write("MIDI_MIN_ARM_VOL = " + self.txt15.get()  + " \n")
            f.write("MIDI_SYNTH_LATENCY = " + self.txt16.get()  + " \n")

            f.write("\n# JOYSTICK CONTROL VARIABLES \n") 
            f.write("JOY_CNX_NUMBER = " + self.txt13.get()  + " \n"  )
            f.write("JOY_BUFF_SIZE = " + self.txt12.get()  + " \n")

        print('the globals.py file has been updated. ')
        print('Taiko Rehab has stopped....  Bye bye ( n o n ) p ')
        sys.exit(-1)

    # check that the introduced value are correct before saving the globals.py file
    def checkBeforeSafe(self):
        max_arm_vol = self.txt14.get()
        min_arm_vol = self.txt15.get()
        midi_latency = self.txt16.get()

        if (not max_arm_vol.isnumeric() or int(max_arm_vol) > 126 ):
            messagebox.showerror(title='Taiko Rehab Error', message="ERROR: max arm values is not number or bigger than 126.")
            return False

        if (not min_arm_vol.isnumeric() or int(min_arm_vol) < 0 ):
            messagebox.showerror(title='Taiko Rehab Error', message="ERROR: min arm values is not number or smaller than 0.")
            return False

        if (not midi_latency.isnumeric()):
            messagebox.showerror(title='Taiko Rehab Error', message="ERROR: MIDI latency value is not a number.")
            return False

        return True


    def openFolder(self,txt):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        fdir = filedialog.askdirectory(initialdir = current_dir)
        if fdir != "":
            txt.delete(0, tk.END)
            txt.insert(0, fdir)

    def openFile(self, txt, filetypes):
        ff = filedialog.askopenfile(filetypes=filetypes)
        if ff is not None:
            txt.delete(0, tk.END)
            txt.insert(0, ff.name)

    def saveAs(self, txt, filetypes):
        ff = filedialog.asksaveasfile(filetypes=filetypes)
        if ff is not None:
            txt.delete(0, tk.END)
            txt.insert(0, ff.name)

    # Toogles the value of all and only good hits, because both options are excluyent 
    def midi_play_all_hits_checked(self):
        self.midi_play_good_hits.set(False) 

    def midi_play_good_hits_checked(self):
        self.midi_play_all_hits.set(False)

    def videoPreProcess(self):
        video_path = self.txt01.get()
        save_csv_path = self.txt02.get()

        # Input paramters check 
        if (os.path.exists(video_path) == False):
            messagebox.showerror(title="Taiko Rehab Error", message="ERROR: Instructor's video file not found." )
            return None

        # Input paramters check 
        # print (save_csv_path)
        # if save_csv_path is None or save_csv_path = "" or os.path.exists:
        if save_csv_path == ""  or os.access(os.path.dirname(save_csv_path), os.W_OK) == False:
            messagebox.showerror(title="Taiko Rehab Error", message="ERROR: Please provide a valid filename to save the arm poses." )
            return None
        
        self.taiko_ctrl.videoPreProcess(video_path, save_csv_path)

    def startTraining(self):
        csv_path =  self.txt1_1.get()
        video_path = self.txt1_2.get()
        midi_path = self.txt1_3.get()
        start_frame = self.txt1_22.get()
        
        # Input parameters check
        if (os.path.exists(csv_path) == False):
            messagebox.showerror(title="Taiko Rehab Error", message="ERROR: Instructor's poses CSV file not found. " )
            return None

        if (os.path.exists(video_path) == False):
            messagebox.showerror(title="Taiko Rehab Error", message="ERROR: Instructor's video file not found. " )
            return None 

        if (os.path.exists(midi_path) == False):
            messagebox.showerror(title="Taiko Rehab Error", message="ERROR: MIDI file not found. " )
            return None

        if (not start_frame.isnumeric()):
            messagebox.showerror(title='Taiko Rehab Error', message="ERROR: Frame number is missing or is not a number.")
            return None
 
        checks = self.taiko_ctrl.initThreads(csv_path, video_path, midi_path, int(start_frame))
        if checks[0] == False:
            messagebox.showerror(title="Taiko Rehab Warning", message="Warning: The Taiko Joystick is not connected to the PC. \nPlease connect it and restart the program." )
        if checks[1] == False:
            messagebox.showerror(title="Taiko Rehab Warning", message="Warning: The M5StickC is not connected to the PC.\n(Force sensor). \nPlease connect it and restart the program." )
        

        self.taiko_ctrl.startTraining()
        

    def showGUI(self):
        self.window = tk.Tk()
        self.window.title("Taiko Rehab v1.0")
        self.window.resizable(False, False)

        tab_control = ttk.Notebook(self.window)
        tab0 = ttk.Frame(tab_control)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)

        tab_control.add(tab0, text='Video Pre-Process')
        tab_control.add(tab1, text='Training')
        tab_control.add(tab2, text='Options')

        ################################  PRE PROCESS ################################################
        lbl01 = ttk.Label(tab0, text= 'This section opens a video file (MP4) and then save the instructor arm poses into a file (CSV).' )
        lbl01.grid(column=0, row=0, columnspan = 2)

        lbl01 = ttk.Label(tab0, text= 'Video MP4 file')
        lbl01.grid(column=0, row=1)
        self.txt01 = ttk.Entry(tab0,width=60)
        self.txt01.insert(tk.END, "")  # for DEBUG ONLY
        self.txt01.grid(column=1, row=1)
        fbtn01 = ttk.Button(tab0, text="Open File", command=(lambda: self.openFile(self.txt01, filetypes=[("Video files", ".mp4")] )))
        fbtn01.grid(column=3, row=1)

        lbl02 = ttk.Label(tab0, text= 'Arm Poses CSV file')
        lbl02.grid(column=0, row=2)
        self.txt02 = ttk.Entry(tab0,width=60)
        self.txt02.insert(tk.END, "")  # for DEBUG ONLY
        self.txt02.grid(column=1, row=2)
        fbtn02 = ttk.Button(tab0, text="Save As", command=(lambda: self.saveAs(self.txt02, filetypes=[("CSV files", ".csv")] )))
        fbtn02.grid(column=3, row=2)


        btn = ttk.Button(tab0, text="Pre Process Poses", command=self.videoPreProcess)
        btn.grid(column=1, row=4)

        ################################  TRAINING ################################################

        lbl11 = ttk.Label(tab1, text= 'Arm Poses CSV file')
        lbl11.grid(column=0, row=0)
        self.txt1_1 = ttk.Entry(tab1,width=60)
        self.txt1_1.insert(tk.END, "./sample7/sample7.csv")  # default value for DEBUG ONLY
        self.txt1_1.grid(column=1, row=0)
        fbtn11 = ttk.Button(tab1, text="Open File", command=(lambda: self.openFile(self.txt1_1, filetypes=[("CSV files", ".csv")] )))
        fbtn11.grid(column=3, row=0)

        lbl12 = ttk.Label(tab1, text= 'Video MP4 file')
        lbl12.grid(column=0, row=1)
        self.txt1_2 = ttk.Entry(tab1,width=60)
        self.txt1_2.insert(tk.END, "./sample7/sample7.mp4")  # default value for DEBUG ONLY
        self.txt1_2.grid(column=1, row=1)
        fbtn12 = ttk.Button(tab1, text="Open File", command=(lambda: self.openFile(self.txt1_2, filetypes=[("Video files", ".mp4")] )))
        fbtn12.grid(column=3, row=1)

        lbl15 = ttk.Label(tab1, text= 'First Note Frame Number')
        lbl15.grid(column=4, row=1)
        self.txt1_22 = ttk.Entry(tab1,width=5)
        self.txt1_22.insert(tk.END, "274")    # default value for DEBUG ONLY
        self.txt1_22.grid(column=5, row=1)

        lbl13 = ttk.Label(tab1, text= 'MIDI File')
        lbl13.grid(column=0, row=2)
        self.txt1_3 = ttk.Entry(tab1,width=60)
        self.txt1_3.insert(tk.END, "./sample7/sample7.mid")  # for DEBUG ONLY
        self.txt1_3.grid(column=1, row=2)
        fbtn13 = ttk.Button(tab1, text="Open File", command=(lambda: self.openFile(self.txt1_3, filetypes=[("MIDI files", ".midi .mid")])))
        fbtn13.grid(column=3, row=2)

        btn = ttk.Button(tab1, text="Start Training", command=self.startTraining)
        btn.grid(column=1, row=4)

        ################################  OPTIONS ################################################

        sep0 = ttk.Separator(tab2, orient='horizontal').grid(column=0, row=0, columnspan=5, ipadx=300)
        lsep0 = ttk.Label(tab2, text="Open Pose options").grid(column=3, row=0)
        
        lbl1 = ttk.Label(tab2, text= 'Open Pose Models Path')
        lbl1.grid(column=0, row=1)
        self.txt1 = ttk.Entry(tab2,width=60)
        self.txt1.insert(tk.END, OP_MODELS_PATH)
        self.txt1.grid(column=1, row=1)
        fbtn1 = ttk.Button(tab2, text="Browse", command=(lambda: self.openFolder(self.txt1)))
        fbtn1.grid(column=3, row=1)

        lbl2 = ttk.Label(tab2, text= 'Open Pose Demo Path')
        lbl2.grid(column=0, row=2)
        self.txt2 = ttk.Entry(tab2,width=60)
        self.txt2.insert(tk.END, OP_PY_DEMO_PATH)
        self.txt2.grid(column=1, row=2)
        fbtn2 = ttk.Button(tab2, text="Browse", command=(lambda: self.openFolder(self.txt2)))
        fbtn2.grid(column=3, row=2)

        sep1 = ttk.Separator(tab2, orient='horizontal').grid(column=0, row=3, columnspan=5, ipadx=300)
        lsep1 = ttk.Label(tab2, text="Open CV options").grid(column=3, row=3)

        lbl3 = ttk.Label(tab2, text= 'OpenCV Camera ID')
        lbl3.grid(column=0, row=4)
        self.combo3 = ttk.Combobox(tab2)
        self.combo3['values'] = (0,1,2,3)
        self.combo3.current(CAM_OPCV_ID)
        self.combo3.grid(column=1, row=4, sticky="W")

        sep3 = ttk.Separator(tab2, orient='horizontal').grid(column=0, row=12, columnspan=5, ipadx=300)
        lsep3 = ttk.Label(tab2, text="MIDI Options").grid(column=3, row=12)

        lbl10 = ttk.Label(tab2, text= 'Time threshold for past GOOD hits (ms)')
        lbl10.grid(column=0, row=13)
        self.txt10 = ttk.Entry(tab2 ,width=50)
        self.txt10.insert(tk.END, MIDI_MAX_PAST)
        self.txt10.grid(column=1, row=13, sticky="w")

        lbl11 = ttk.Label(tab2, text= 'Time threshold for future GOOD hits (ms)')
        lbl11.grid(column=0, row=14)
        self.txt11 = ttk.Entry(tab2 ,width=50)
        self.txt11.insert(tk.END, MIDI_MAX_FUTURE)
        self.txt11.grid(column=1, row=14, sticky="w")


        lbl17 = ttk.Label(tab2, text= 'Max MIDI vol. for max arm height (max 126)')
        lbl17.grid(column=0, row=15)
        self.txt14 = ttk.Entry(tab2 ,width=50)
        self.txt14.insert(tk.END, MIDI_MAX_ARM_VOL)
        self.txt14.grid(column=1, row=15, sticky="w")

        lbl18 = ttk.Label(tab2, text= 'Min MIDI vol. for min arm height (min 0)')
        lbl18.grid(column=0, row=16)
        self.txt15 = ttk.Entry(tab2 ,width=50)
        self.txt15.insert(tk.END, MIDI_MIN_ARM_VOL)
        self.txt15.grid(column=1, row=16, sticky="w")

        lbl19 = ttk.Label(tab2, text= 'Windows MIDI Synth latency value (in ms)')
        lbl19.grid(column=0, row=17)
        self.txt16 = ttk.Entry(tab2 ,width=50)
        self.txt16.insert(tk.END, MIDI_SYNTH_LATENCY)
        self.txt16.grid(column=1, row=17, sticky="w")

        lbl16 = ttk.Label(tab2, text= 'Joystick ID number')
        lbl16.grid(column=0, row=18)
        self.txt13 = ttk.Entry(tab2 ,width=50)
        self.txt13.insert(tk.END, JOY_CNX_NUMBER)
        self.txt13.grid(column=1, row=18, sticky="w")

        lbl12 = ttk.Label(tab2, text= 'Joystick inputs buffer size')
        lbl12.grid(column=0, row=19)
        self.txt12 = ttk.Entry(tab2 ,width=50)
        self.txt12.insert(tk.END, JOY_BUFF_SIZE)
        self.txt12.grid(column=1, row=19, sticky="w")

        self.midi_play_good_hits = tk.BooleanVar(value = MIDI_PLAY_GOOD_HITS)
        check1 = tk.Checkbutton(tab2, text = "Play only GOOD timming drum hits",  variable=self.midi_play_good_hits, command=self.midi_play_good_hits_checked )
        check1.grid(column=0, row=20)

        self.midi_play_all_hits = tk.BooleanVar(value = MIDI_PLAY_ALL_HITS)
        check2 = tk.Checkbutton(tab2, text = "Play ALL drum hits",  variable=self.midi_play_all_hits, command=self.midi_play_all_hits_checked  )
        check2.grid(column=1, row=21)

        self.midi_play_file_notes = tk.BooleanVar(value = MIDI_PLAY_MIDIFILE_NOTES)
        check3 = tk.Checkbutton(tab2, text = "Play notes from MIDI file",  variable=self.midi_play_file_notes )
        check3.grid(column=2, row=22)

        sep4 = ttk.Separator(tab2, orient='horizontal').grid(column=0, row=23, columnspan=5, ipadx=300)
        lsep4 = ttk.Label(tab2, text="Training  options").grid(column=3, row=23)

        # THIS ELEMENT INDEXES ARE OUT OF ORDER (cut and pasted into other section)
        lbl4 = ttk.Label(tab2, text= 'Max Frames for Visual Feedback')
        lbl4.grid(column=0, row=24)
        self.txt4 = ttk.Entry(tab2 ,width=50)
        self.txt4.insert(tk.END, MAX_TXT_FRAMES)
        self.txt4.grid(column=1, row=24, sticky="W")

        self.draw_sensei_arms = tk.BooleanVar(value = DRAW_SENSEI_ARMS)
        check4 = tk.Checkbutton(tab2, text = "Draw Sensei arms over User", variable=self.draw_sensei_arms )
        check4.grid(column=0, row=27)

        self.draw_hits = tk.BooleanVar(value = DRAW_HITS)
        check5 = tk.Checkbutton(tab2, text = "Draw User's hits feedback", variable=self.draw_hits )
        check5.grid(column=1, row=27)

        # lbl10 = ttk.Label(tab2, text= 'Visual Feedback')
        # lbl10.grid(column=0, row=13)

        # self.instructor = tk.BooleanVar(value = True)
        # check0 = tk.Checkbutton(tab2, text = "Show Instructor Video", variable=self.instructor )
        # check0.grid(column=0, row=13)

        # self.user_camera = tk.BooleanVar(value = True)
        # check1 = tk.Checkbutton(tab2, text = "Show User Camera",  variable=self.user_camera )
        # check1.grid(column=1, row=13)

        # self.visual_feedback = tk.BooleanVar(value = True)
        # check2 = tk.Checkbutton(tab2, text = "Show Visual Feedback",  variable=self.visual_feedback )
        # check2.grid(column=2, row=13)

        btn = ttk.Button(tab2, text="Save & Close", command=self.save)
        btn.grid(column=1, row=33)

        tab_control.pack(expand=1, fill='both')
        self.window.mainloop()


def main():
    # Class of the main program control
    taiko_ctrl = taikoControl()

    # Creates class just for GUI control
    gui = taikoGUI(taiko_ctrl)
    gui.showGUI()


if __name__ == "__main__":
    main()


