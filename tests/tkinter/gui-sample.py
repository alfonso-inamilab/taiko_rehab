from tkinter import *
from tkinter import ttk

# IMPORTING GLOBAL PARAMETERS 
from include.globals import OP_PY_DEMO_PATH
from include.globals import OP_MODELS_PATH
from include.globals import CAM_OPCV_ID
from include.globals import MAX_NUM_PEOPLE
from include.globals import MAX_TXT_FRAMES
from include.globals import FULL_LOG_FILE
from include.globals import FORCE_LOG_NAME
from include.globals import ARMS_LOG_NAME

# # OPENCV GLOBAL VARIABLES 
# OP_MODELS_PATH = "C:\\openpose\\openpose\\models\\" # OpenPose models folder
# OP_PY_DEMO_PATH = "C:\\openpose\\openpose\\build\\examples\\tutorial_api_python\\"  # OpenPose 
# CAM_OPCV_ID = 0    # Open CV camera ID   (IS NOT USED ANYMORE)
# MAX_TXT_FRAMES = 5  # Number of frames the text wrist will be in the screen
# MAX_NUM_PEOPLE = 1  # Nuber of users detected with OpenCV. -1 for No limit

# # PROGRAM GLOBAL VARIABLES
# FULL_LOG_FILE =  'full_log.csv'
# FORCE_LOG_NAME = 'force_log.csv' 
# ARMS_LOG_NAME =  'arm_angle_log.csv'

def save():
    res = "Welcome to " + txt.get()
    lbl.configure(text= res)

def loadJson():
    pass

window = Tk()
window.title("Tabs Samples")

tab_control = ttk.Notebook(window)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)

tab_control.add(tab1, text='Start')
tab_control.add(tab2, text='Options')

lbl1 = Label(tab2, text= 'Open Pose Models Path')
lbl1.grid(column=0, row=0)
txt1 = Entry(tab2,width=60)
txt1.grid(column=1, row=0)
lbl2 = Label(tab2, text= 'Open Pose Demo Path')
lbl2.grid(column=0, row=1)
txt2 = Entry(tab2,width=60)
txt2.grid(column=1, row=1)

lbl3 = Label(tab2, text= 'Camera Open CV ID')
lbl3.grid(column=0, row=2)
combo3 = ttk.Combobox(tab2)
combo3['values'] = (0,1,2,3)
combo3.grid(column=1, row=2, sticky="W")

lbl4 = Label(tab2, text= 'Max Frames for Text')
lbl4.grid(column=0, row=3)
txt4 = Entry(tab2 ,width=50)
txt4.grid(column=1, row=3, sticky="W")

lbl5 = Label(tab2, text= 'Max Number of People')
lbl5.grid(column=0, row=4)
txt5 = Entry(tab2 ,width=50, text="1")
txt5.grid(column=1, row=4, sticky="W")


lbl6 = Label(tab2, text= 'Full log CSV file name')
lbl6.grid(column=0, row=6)
txt6 = Entry(tab2 ,width=50)
txt6.insert(END, include.FULL_LOG_FILE)
txt6.grid(column=1, row=6, sticky="W")


lbl7 = Label(tab2, text= 'Force log CSV file name')
lbl7.grid(column=0, row=7)
txt7 = Entry(tab2 ,width=50)
txt7.insert(END, include.FORCE_LOG_NAME)
txt7.grid(column=1, row=7, sticky="W")


lbl8 = Label(tab2, text= 'Arms log CSV file name')
lbl8.grid(column=0, row=8)
txt8 = Entry(tab2 ,width=50)
txt8.insert(END, include.ARMS_LOG_NAME)
txt8.grid(column=1, row=8, sticky="W")


btn = Button(tab2, text="Save", command=save)
btn.grid(column=1, row=10)

tab_control.pack(expand=1, fill='both')
window.mainloop()