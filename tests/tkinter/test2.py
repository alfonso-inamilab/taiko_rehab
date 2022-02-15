import sys
import cv2
import time
import math
import os
from sys import platform
import argparse
import pygame
import ctypes
import numpy as np
from multiprocessing import Array, Value



from tkinter import Tk
from tkinter import ttk
from tkinter import filedialog

class Test1():
    def __init__(self):
        self.window = None
        self.txt1 = None
    
    # def showGUI(self):
    #     root = Tk()
    #     root.withdraw()

    #     current_directory = filedialog.askdirectory()
    #     file_name = "test.txt"

    #     file_path = os.path.join(current_directory,file_name)
    #     print(file_path)

    def openFolder(self):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        dir_path = filedialog.askdirectory(initialdir=current_dir)
        entry_ws.set(dir_path)


    def showGUI(self):
        self.window = Tk()
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
        # fbtn11 = ttk.Button(tab1, text="Open File", command=(lambda: self.openFolder( )))
        fbtn11 = ttk.Button(tab1, text="Open File", command=self.openFolder)
        fbtn11.grid(column=3, row=0)

        tab_control.pack(expand=1, fill='both')
        self.window.mainloop()


def main():
    test = Test1()
    test.showGUI()


if __name__ == "__main__":
    main()



