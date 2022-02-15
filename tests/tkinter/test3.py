import os

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

# IMPORTING GLOBAL PARAMETERS 
from include.globals import OP_PY_DEMO_PATH
from include.globals import OP_MODELS_PATH
from include.globals import CAM_OPCV_ID
from include.globals import MAX_NUM_PEOPLE
from include.globals import MAX_TXT_FRAMES
from include.globals import FULL_LOG_FILE
from include.globals import FORCE_LOG_NAME
from include.globals import ARMS_LOG_NAME

# IMPORT CLASS FOR THE TAIKO MAIN PROGRAM CONTROL
# from taiko_control import taikoControl

import sys
import cv2
import os
import time
import math
from sys import platform
import argparse
import pygame
import ctypes
import numpy as np
from multiprocessing import Array, Value

# IMPORTING GLOBAL PARAMETERS 
from include.globals import OP_PY_DEMO_PATH
from include.globals import OP_MODELS_PATH
from include.globals import CAM_OPCV_ID
from include.globals import MAX_NUM_PEOPLE
from include.globals import MAX_TXT_FRAMES
from include.globals import FULL_LOG_FILE
from include.globals import ARMS_LOG_NAME
from include.globals import FORCE_LOG_NAME

# TAIKO REHAB MODULES
from include.cameraThread import camThread
# PYGAME JOYSTICK TO CATCH TIME EVENTS
from include.joystick import Joystick
# MIDO TO PLAY MIDI AND MEASURE TIMMING
from include.midi_control import MidiControl
# CLASS TO CALCULATE AND LOG ARMS AND SHOULDERS POSITION
from include.arm_angle_logger import ArmAngleLog
# CLASS TO READ THE FORCE/ACC FROM THE SENSOR
from include.m5stick_serial_acc import M5SerialCom
# CLASS TO DISPLAY SIMULTANEOUS VIDEO DISPLAY 
from include.video_display import VideoDisplay

class taikoGUI():

    def __init__(self,taiko_ctrl):
        self.txt1 = None
        self.txt2 = None
        self.txt4 = None
        self.txt5 = None
        self.txt6 = None
        self.txt7 = None
        self.txt8 = None
        self.txt11 = None
        self.txt12 = None
        self.txt13 = None
        self.combo3 = None
        self.taiko_ctrl = taiko_ctrl

    # save the config file direclty re-writing the global.py file
    def save(self):
        with open('include/globals.py', 'w') as f:
            f.write("# OPENCV GLOBAL VARIABLES \n")
            f.write("OP_MODELS_PATH = \""  + self.txt1.get().replace('\\','\\\\') +  "\" # OpenPose models folder \n")
            f.write("OP_PY_DEMO_PATH = \""  + self.txt2.get().replace('\\','\\\\') +  "\" # OpenPose demo folder \n")
            f.write("CAM_OPCV_ID = " + self.combo3.get() +   " # Open CV camera ID \n" )
            f.write("MAX_TXT_FRAMES = " + self.txt4.get()  + " # Number of frames the text wrist will be in the screen \n")
            f.write("MAX_NUM_PEOPLE = " + self.txt5.get()  + " # Nuber of users detected with OpenCV. -1 for No limit \n")

            f.write("\n# PROGRAM GLOBAL VARIABLES \n") 
            f.write("FULL_LOG_FILE = \"" + self.txt6.get().replace('\\','\\\\')  + "\" \n")
            f.write("FORCE_LOG_NAME = \"" + self.txt7.get().replace('\\','\\\\')  + "\" \n")
            f.write("ARMS_LOG_NAME = \"" + self.txt8.get().replace('\\','\\\\')  + "\" \n")

    def openFolder(self):
        self.window.update()
        current_dir = os.path.abspath(os.path.dirname(__file__))
        dir_path = filedialog.askdirectory(initialdir=current_dir)
        entry_ws.set(dir_path)

        # folder = filedialog.askdirectory(initialdir=os.path.normpath("C://"), title="Example")
        # folder = filedialog.askdirectory()

        # self.window.update()
        # self.window.withdraw()
        # current_dir = os.path.abspath(os.path.dirname(__file__))
        # fdir = filedialog.askdirectory(initialdir = current_dir)
        # if fdir != "":
        #     txt.delete(0, END)
        #     txt.insert(0, fdir)

    def openFile(self, txt, filetypes):
        ff = filedialog.askopenfile(filetypes=filetypes)
        if ff is not None:
            txt.delete(0, END)
            txt.insert(0, ff.name)

    def getPaths(self):
        # returns [video csv file, video file, midi file ]
        return [self.txt11.get(), self.txt12.get(), self.txt13.get()]

    def startTraining(self):
        # csv_path =  self.txt11.get()
        # video_path = self.txt12.get()
        # midi_path = self.txt13.get()
        csv_path = "./samples/sample1-1.csv"
        video_path = "./samples/sample1-1.mp4"
        midi_path = "./samples/sample1-1.mid"

        # Input parameters check
        if (os.path.exists(csv_path) == False):
            messagebox.showerror(title="Taiko Rehab Error", message="ERROR: Instructor's poses CSV file was not found. [" + csv_path + ".csv" + "]" )
            return None

        if (os.path.exists(video_path) == False):
            messagebox.showerror(title="Taiko Rehab Error", message="ERROR: Instructor's video file was not found. [" + video_path + ".csv" + "]" )
            return None 

        if (os.path.exists(midi_path) == False):
            messagebox.showerror(title="Taiko Rehab Error", message="ERROR: MIDI file was not found. [" + midi_path + ".csv" + "]" )
            return None

        self.taiko_ctrl.initThreads(csv_path, video_path, midi_path)
        self.taiko_ctrl.startTraining()
        

    def showGUI(self):
        self.window = tk.Tk()
        self.window.title("Taiko Rehab v1.0")

        tab_control = ttk.Notebook(self.window)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)

        tab_control.add(tab1, text='Training')
        tab_control.add(tab2, text='Options')

        ################################  TRAINING ################################################

        lbl11 = ttk.Label(tab1, text= 'Video CSV file')
        lbl11.grid(column=0, row=0)
        self.txt11 = ttk.Entry(tab1,width=60)
        self.txt11.grid(column=1, row=0)
        fbtn11 = ttk.Button(tab1, text="Open File", command=(lambda: self.openFile(self.txt11, filetypes=[("CSV files", ".csv")] )))
        fbtn11.grid(column=3, row=0)

        lbl12 = ttk.Label(tab1, text= 'Video MP4 file')
        lbl12.grid(column=0, row=1)
        self.txt12 = ttk.Entry(tab1,width=60)
        self.txt12.grid(column=1, row=1)
        fbtn12 = ttk.Button(tab1, text="Open File", command=(lambda: self.openFile(self.txt12, filetypes=[("Video files", ".mp4")] )))
        fbtn12.grid(column=3, row=1)

        lbl13 = ttk.Label(tab1, text= 'MIDI File')
        lbl13.grid(column=0, row=2)
        self.txt13 = ttk.Entry(tab1,width=60)
        self.txt13.grid(column=1, row=2)
        fbtn13 = ttk.Button(tab1, text="Open File", command=(lambda: self.openFile(self.txt13, filetypes=[("MIDI files", ".midi .mid")])))
        fbtn13.grid(column=3, row=2)

        btn = ttk.Button(tab1, text="Start Training", command=self.startTraining)
        btn.grid(column=1, row=4)

        ################################  OPTIONS ################################################

        lbl1 = ttk.Label(tab2, text= 'Open Pose Models Path')
        lbl1.grid(column=0, row=0)
        self.txt1 = ttk.Entry(tab2,width=60)
        # self.txt1.insert(END, OP_MODELS_PATH)
        self.txt1.grid(column=1, row=0)
        # fbtn1 = Button(tab2, text="Browse", command=(lambda: self.openFolder()))
        fbtn1 = ttk.Button(tab2, text="Browse", command=self.openFolder )
        fbtn1.grid(column=3, row=0)

        lbl2 = ttk.Label(tab2, text= 'Open Pose Demo Path')
        lbl2.grid(column=0, row=1)
        self.txt2 = ttk.Entry(tab2,width=60)
        # self.txt2.insert(END, OP_PY_DEMO_PATH)
        self.txt2.grid(column=1, row=1)
        fbtn2 = ttk.Button(tab2, text="Browse", command=(lambda: self.openFolder()))
        fbtn2.grid(column=3, row=1)

        lbl3 = ttk.Label(tab2, text= 'OpenCV Camera ID')
        lbl3.grid(column=0, row=2)
        self.combo3 = ttk.Combobox(tab2)
        self.combo3['values'] = (0,1,2,3)
        self.combo3.current(CAM_OPCV_ID)
        self.combo3.grid(column=1, row=2, sticky="W")

        lbl4 = ttk.Label(tab2, text= 'Max Frames for Text')
        lbl4.grid(column=0, row=3)
        self.txt4 = ttk.Entry(tab2 ,width=50)
        self.txt4.insert(tk.END, MAX_TXT_FRAMES)
        self.txt4.grid(column=1, row=3, sticky="W")

        lbl5 = ttk.Label(tab2, text= 'Max Number of People')
        lbl5.grid(column=0, row=4)
        self.txt5 = ttk.Entry(tab2 ,width=50)
        self.txt5.insert(tk.END, MAX_NUM_PEOPLE)
        self.txt5.grid(column=1, row=4, sticky="W")


        lbl6 = ttk.Label(tab2, text= 'Full log CSV file name')
        lbl6.grid(column=0, row=6)
        self.txt6 = ttk.Entry(tab2 ,width=50)
        self.txt6.insert(tk.END, FULL_LOG_FILE)
        self.txt6.grid(column=1, row=6, sticky="W")


        lbl7 = ttk.Label(tab2, text= 'Force log CSV file name')
        lbl7.grid(column=0, row=7)
        self.txt7 = ttk.Entry(tab2 ,width=50)
        self.txt7.insert(tk.END, FORCE_LOG_NAME)
        self.txt7.grid(column=1, row=7, sticky="W")


        lbl8 = ttk.Label(tab2, text= 'Arms log CSV file name')
        lbl8.grid(column=0, row=8)
        self.txt8 = ttk.Entry(tab2 ,width=50)
        self.txt8.insert(tk.END, ARMS_LOG_NAME)
        self.txt8.grid(column=1, row=8, sticky="W")


        btn = ttk.Button(tab2, text="Save", command=self.save)
        btn.grid(column=1, row=10)

        tab_control.pack(expand=1, fill='both')
        self.window.mainloop()


def main():
    # Class of the main program control
    # taiko_ctrl = taikoControl()

    # Creates class just for GUI control.
    # gui = taikoGUI(taiko_ctrl) 
    gui = taikoGUI(None)
    gui.showGUI()


if __name__ == "__main__":
    main()


