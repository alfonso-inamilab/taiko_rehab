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
from include.globals import FULL_LOG_FILE
from include.globals import FORCE_LOG_NAME
from include.globals import ARMS_LOG_NAME
from include.globals import MIDI_LOG_NAME
from include.globals import MIDI_MAX_PAST
from include.globals import MIDI_MAX_FUTURE
from include.globals import MIDI_PLAY_HITS
from include.globals import MIDI_PLAY_ALL_NOTES
from include.globals import MIDI_INS_CH
from include.globals import MIDI_DRUMS_CH
from include.globals import DRAW_SENSEI_ARMS


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
        # Option section GUI objects
        self.txt1 = None
        self.txt2 = None
        self.txt4 = None
        self.txt5 = None
        self.txt6 = None
        self.txt7 = None
        self.txt8 = None
        self.txt9 = None
        self.txt11 = None
        self.txt12 = None
        self.txt13 = None
        self.txt14 = None
        self.midi_play_all = None
        self.midi_play_hits = None
        self.draw_sensei_arms = None

        self.combo3 = None
        self.instructor = None
        self.visual_feedback = None
        self.user_camera = None
        # Class to control the other clases
        self.taiko_ctrl = taiko_ctrl

    # save the config file direclty re-writing the global.py file
    def save(self):
        with open('include/globals.py', 'w') as f:
            f.write("# OPENCV GLOBAL VARIABLES \n")
            f.write("OP_MODELS_PATH = \""  + self.txt1.get().replace('\\','\\\\') +  "\" # OpenPose models folder \n")
            f.write("OP_PY_DEMO_PATH = \""  + self.txt2.get().replace('\\','\\\\') +  "\" # OpenPose demo folder \n")
            f.write("CAM_OPCV_ID = " + self.combo3.get() +   " # Open CV camera ID \n" )
            f.write("MAX_TXT_FRAMES = " + self.txt4.get()  + " # Number of frames the text wrist will be in the screen \n")

            f.write("\n# PROGRAM GLOBAL VARIABLES \n") 
            f.write("FULL_LOG_FILE = \"" + self.txt6.get().replace('\\','\\\\')  + "\" \n")
            f.write("FORCE_LOG_NAME = \"" + self.txt7.get().replace('\\','\\\\')  + "\" \n")
            f.write("ARMS_LOG_NAME = \"" + self.txt8.get().replace('\\','\\\\')  + "\" \n")
            f.write("MIDI_LOG_NAME = \"" + self.txt9.get().replace('\\','\\\\')  + "\" \n")
            f.write("DRAW_SENSEI_ARMS = " + str(self.draw_sensei_arms.get())  + " \n")



            f.write("\n# MIDI CONTROL VARIABLES \n") 
            f.write("MIDI_MAX_PAST = "  + self.txt10.get()  + " \n")
            f.write("MIDI_MAX_FUTURE = " + self.txt11.get()  + " \n")
            f.write("MIDI_PLAY_HITS = " + str(self.midi_play_hits.get())  + " \n")
            f.write("MIDI_PLAY_ALL_NOTES = " + str(self.midi_play_all.get())  + " \n")
            f.write("MIDI_INS_CH = "  + self.txt12.get()  + " \n")
            f.write("MIDI_DRUMS_CH = " + self.txt13.get()  + " \n")


        print('Taiko Rehab has stopped....  Bye bye ( n o n ) p ')
        sys.exit(-1)

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
        # csv_path = "./samples/sample1-1.csv"
        # video_path = "./samples/sample1-1.mp4"
        # midi_path = "./samples/sample1.mid"

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

        self.taiko_ctrl.initThreads(csv_path, video_path, midi_path)
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
        self.txt1_1.insert(tk.END, "./samples/sample1.csv")  # for DEBUG ONLY
        self.txt1_1.grid(column=1, row=0)
        fbtn11 = ttk.Button(tab1, text="Open File", command=(lambda: self.openFile(self.txt1_1, filetypes=[("CSV files", ".csv")] )))
        fbtn11.grid(column=3, row=0)

        lbl12 = ttk.Label(tab1, text= 'Video MP4 file')
        lbl12.grid(column=0, row=1)
        self.txt1_2 = ttk.Entry(tab1,width=60)
        self.txt1_2.insert(tk.END, "./samples/sample1.mp4")  # for DEBUG ONLY
        self.txt1_2.grid(column=1, row=1)
        fbtn12 = ttk.Button(tab1, text="Open File", command=(lambda: self.openFile(self.txt1_2, filetypes=[("Video files", ".mp4")] )))
        fbtn12.grid(column=3, row=1)

        lbl13 = ttk.Label(tab1, text= 'MIDI File')
        lbl13.grid(column=0, row=2)
        self.txt1_3 = ttk.Entry(tab1,width=60)
        self.txt1_3.insert(tk.END, "./samples/sample1.mid")  # for DEBUG ONLY
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

        sep2 = ttk.Separator(tab2, orient='horizontal').grid(column=0, row=7, columnspan=5, ipadx=300)
        lsep2 = ttk.Label(tab2, text="Data log options").grid(column=3, row=7)

        lbl6 = ttk.Label(tab2, text= 'Full log CSV file name')
        lbl6.grid(column=0, row=8)
        self.txt6 = ttk.Entry(tab2 ,width=50)
        self.txt6.insert(tk.END, FULL_LOG_FILE)
        self.txt6.grid(column=1, row=8, sticky="W")

        lbl7 = ttk.Label(tab2, text= 'Force log CSV file name')
        lbl7.grid(column=0, row=9)
        self.txt7 = ttk.Entry(tab2 ,width=50)
        self.txt7.insert(tk.END, FORCE_LOG_NAME)
        self.txt7.grid(column=1, row=9, sticky="W")

        lbl8 = ttk.Label(tab2, text= 'Arms log CSV file name')
        lbl8.grid(column=0, row=10)
        self.txt8 = ttk.Entry(tab2 ,width=50)
        self.txt8.insert(tk.END, ARMS_LOG_NAME)
        self.txt8.grid(column=1, row=10, sticky="W")

        lbl9 = ttk.Label(tab2, text= 'MIDI time log CSV file name')
        lbl9.grid(column=0, row=11)
        self.txt9 = ttk.Entry(tab2 ,width=50)
        self.txt9.insert(tk.END, MIDI_LOG_NAME)
        self.txt9.grid(column=1, row=11, sticky="W")

        sep3 = ttk.Separator(tab2, orient='horizontal').grid(column=0, row=12, columnspan=5, ipadx=300)
        lsep3 = ttk.Label(tab2, text="MIDI Options").grid(column=3, row=12)

        lbl10 = ttk.Label(tab2, text= 'Time threshold for prev. for GOOD hits (ms)')
        lbl10.grid(column=0, row=13)
        self.txt10 = ttk.Entry(tab2 ,width=50)
        self.txt10.insert(tk.END, MIDI_MAX_PAST)
        self.txt10.grid(column=1, row=13, sticky="w")

        lbl11 = ttk.Label(tab2, text= 'Time threshold for future for GOOD hits (ms)')
        lbl11.grid(column=0, row=14)
        self.txt11 = ttk.Entry(tab2 ,width=50)
        self.txt11.insert(tk.END, MIDI_MAX_FUTURE)
        self.txt11.grid(column=1, row=14, sticky="w")

        lbl12 = ttk.Label(tab2, text= 'Hits MIDI Channel (normal instrument 1ch-8ch)')
        lbl12.grid(column=0, row=15)
        self.txt12 = ttk.Entry(tab2 ,width=50)
        self.txt12.insert(tk.END, MIDI_INS_CH)
        self.txt12.grid(column=1, row=15, sticky="w")

        lbl13 = ttk.Label(tab2, text= 'Hits MIDI Channel (drums 9ch-16ch)')
        lbl13.grid(column=0, row=16)
        self.txt13 = ttk.Entry(tab2 ,width=50)
        self.txt13.insert(tk.END, MIDI_DRUMS_CH)
        self.txt13.grid(column=1, row=16, sticky="w")


        self.midi_play_hits = tk.BooleanVar(value = MIDI_PLAY_HITS)
        check1 = tk.Checkbutton(tab2, text = "Play user's GOOD hits",  variable=self.midi_play_hits )
        check1.grid(column=0, row=17)
        
        self.midi_play_all = tk.BooleanVar(value = MIDI_PLAY_ALL_NOTES)
        check2 = tk.Checkbutton(tab2, text = "Play All MIDI Notes (DEBUG ONLY)",  variable=self.midi_play_all )
        check2.grid(column=1, row=17)

        sep4 = ttk.Separator(tab2, orient='horizontal').grid(column=0, row=18, columnspan=5, ipadx=300)
        lsep4 = ttk.Label(tab2, text="Training  options").grid(column=3, row=18)

        lbl4 = ttk.Label(tab2, text= 'Max Frames for Visual Feedback')
        lbl4.grid(column=0, row=19)
        self.txt4 = ttk.Entry(tab2 ,width=50)
        self.txt4.insert(tk.END, MAX_TXT_FRAMES)
        self.txt4.grid(column=1, row=19, sticky="W")

        self.draw_sensei_arms = tk.BooleanVar(value = DRAW_SENSEI_ARMS)
        check3 = tk.Checkbutton(tab2, text = "Draw Sensei arms over User", variable=self.draw_sensei_arms )
        check3.grid(column=0, row=25)

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
        btn.grid(column=1, row=20)

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


