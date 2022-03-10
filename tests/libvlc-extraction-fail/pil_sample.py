# SAMPLES TAKEN FROM 
# USE PIL TO OPEN LIBVLC CTYPES BUFFER


# TRANSFORM PIL IMAGE TO OPENCV FORMAT (
# https://qiita.com/derodero24/items/f22c22b22451609908ee

import vlc
import ctypes
import time
import sys
import numpy as np
import cv2

from PIL import Image

pl = vlc.MediaPlayer('C:/rehab/src/taiko_rehab/src/samples/sample1.mp4')

VIDEOWIDTH = 1280
VIDEOHEIGHT = 720

OP_MODELS_PATH = "C:/openpose/openpose/models/" # OpenPose models folder 
OP_PY_DEMO_PATH = "C:/openpose/openpose/build/examples/tutorial_api_python/" # OpenPose demo folder 

# size in bytes when RV32
size = VIDEOWIDTH * VIDEOHEIGHT * 4
# allocate buffer
buf = (ctypes.c_ubyte * size)()
# get pointer to buffer
buf_p = ctypes.cast(buf, ctypes.c_void_p)

# global frame (or actually displayed frame) counter
framenr = 0
vtime = 0

# vlc.CallbackDecorators.VideoLockCb is incorrect
CorrectVideoLockCb = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))

# INIT OpenCV block
try:       
    # Change these variables to point to the correct folder (Release/x64 etc.)
    sys.path.append(OP_PY_DEMO_PATH + '/../../python/openpose/Release')
    os.environ['PATH']  = os.environ['PATH'] + ';' + OP_PY_DEMO_PATH + '/../../x64/Release;' +  OP_PY_DEMO_PATH + '/../../bin;'
    import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e

params = dict()
params["model_folder"] = OP_MODELS_PATH
params["number_people_max"] = 1 #MAX_NUM_PEOPLE

# Init OpenPose python wrapper
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()
datum = op.Datum()
# INIT OpenCV block

@CorrectVideoLockCb
def _lockcb(opaque, planes):
    # print("lock", file=sys.stderr)
    planes[0] = buf_p

# MY MODIFIED FUNCTION TO USE OPENCV INSTEAD 
# process all the frames, not just every 24 frames
@vlc.CallbackDecorators.VideoDisplayCb
def _display(opaque, picture):
    global framenr
    global vtime
    print("frame {}".format(framenr))
    print("time", vtime)

    img = Image.frombuffer("RGBA", (VIDEOWIDTH, VIDEOHEIGHT), buf, "raw", "BGRA", 0, 1)
    new_image = np.array(img, dtype=np.uint8)
    new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    # cv2.imwrite('img{}.png'.format(framenr), new_image)
    cv2.imshow("pil sample", new_image)
    key = cv2.waitKey(1)

    framenr += 1
    vtime = pl.get_time()


vlc.libvlc_video_set_callbacks(pl, _lockcb, None, _display, None)
pl.video_set_format("RV32", VIDEOWIDTH, VIDEOHEIGHT, VIDEOWIDTH * 4)

pl.play()
# pl.play()
# time.sleep(10)
while True:
    pass