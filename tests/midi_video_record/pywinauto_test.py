import pywinauto
import time
import subprocess
import os
import datetime

class videoRecord():

    def __init__(self):
        pass 
    
    def win_record(self, duration):
        subprocess.run('start microsoft.windows.camera:', shell=True)  # open camera app

        # focus window by getting handle using title and class name
        # subprocess call opens camera and gets focus, but this provides alternate way
        # t, c = 'Camera', 'ApplicationFrameWindow'
        # handle = pywinauto.findwindows.find_windows(title=t, class_name=c)[0]
        # # get app and window
        # app = pywinauto.application.Application().connect(handle=handle)
        # window = app.window(handle=handle)
        # window.set_focus()  # set focus
        time.sleep(2)  # have to sleep

        # take control of camera window to take video
        desktop = pywinauto.Desktop(backend="uia")
        cam = desktop['Camera']
        # cam.print_control_identifiers()
        # make sure in video mode
        if cam.child_window(title="Switch to Video mode", auto_id="CaptureButton_1", control_type="Button").exists():
            cam.child_window(title="Switch to Video mode", auto_id="CaptureButton_1", control_type="Button").click()
        time.sleep(1)
        # start then stop video
        cam.child_window(title="Take Video", auto_id="CaptureButton_1", control_type="Button").click()
        time.sleep(duration+2)
        cam.child_window(title="Stop taking Video", auto_id="CaptureButton_1", control_type="Button").click()

        # retrieve vids from camera roll and sort
        dir = 'C:/Users/ponch/Pictures/Camera Roll'
        all_contents = list(os.listdir(dir))
        vids = [f for f in all_contents if "_Pro.mp4" in f]
        vids.sort()
        vid = vids[-1]  # get last vid
        # compute time difference
        vid_time = vid.replace('WIN_', '').replace('_Pro.mp4', '')
        vid_time = datetime.datetime.strptime(vid_time, '%Y%m%d_%H_%M_%S')
        now = datetime.datetime.now()
        diff = now - vid_time
        # time different greater than duration plus 1 minute, assume something wrong & quit
        if diff.seconds > (duration * 60 + 60):
            quit()
        
        subprocess.run('Taskkill /IM WindowsCamera.exe /F', shell=True)  # close camera app
        print('Recorded successfully!')


r = videoRecord()
r.win_record(2)