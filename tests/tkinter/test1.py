import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

root = tk.Tk()
root.geometry("200x100")

def dirdialog_clicked():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    dir_path = filedialog.askdirectory(initialdir=current_dir)
    entry_ws.set(dir_path)

entry_ws = tk.StringVar()
dir_entry = ttk.Entry(root, textvariable=entry_ws, width=20)
dir_entry.pack(side=tk.LEFT)

dir_button = ttk.Button(root, text="参照", command=dirdialog_clicked)
dir_button.pack(side=tk.LEFT)

root.mainloop()