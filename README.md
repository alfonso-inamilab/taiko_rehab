# Taiko Rehab
Cognitive and physical rehabilitation system for old people by playing Taiko

## System description
Taiko Rehab uses a MIDI file and a video file of an instructor playing the Taiko. When the music starts, Taiko Rehab plays the MIDI and video file together, while the system registers the user's shoulders and arms positions, the hitting timming and the force. Finally when the program is closed, all the data is dumped into a CSV file for later analysis. 

![System Description](img/system_description.png?raw=true)

## Usage 

First it is necessary to pre-process the instructor's video file (MP4) to save his arm poses in a CSV file. 
For this, in the `Video Pre_Process section` open the MP4 and select a name for the CSV file.
Then click `Pre Process Poses` and wuit until the video finish. 

![Pre-Process Screen](img/pre-process-screen.png?raw=true)

With the sensei's video (MP4), drum hits (MIDI) and poses (CSV), go to section `Training` open the MP4,MIDI and CSV files.
Then indicate the frame number of the first MIDI note. And then click `Start Training`. 

![Pre-Process Screen](img/training-screen.png?raw=true)

This will open the users' camera on a screen. Then press `p` to start the Taiko Drum training. 
To close the program press `q` or `ESC` on the user's webcam screen. 

## Hardware

The sensor used for this are: 
- Taiko joystick to measure hit timming 
https://www.amazon.co.jp/gp/product/B07T9DZBW9
- Accelerometer to measure hit force (MPU6050 attached to Taiko Joystick)
 https://www.amazon.co.jp/-/en/gp/product/B07MPBMRWD/ref=ox_sc_act_title_1?smid=A3ALF3N55UI5NK&psc=1
- Web Camera to measure the wrist position with OpenPose


## Event Log Description 

### Arms Information log (`arms_log.csv`)
| Colum Name  |      Description      |  Type |
|----------|:-------------:|------:|
| Index |  Index of each event | integer |
| Time(epoch ms) |  The PC epoch time when the event happen. (in milliseconds) | long |
| Left_Sh_Angle(deg) |  Angle between the left shoulder and left arm (in degrees) | float |
| Right_Sh_Angle(deg) |  Angle between the right shoulder and right arm (in degrees) | float |
| Left_Arm_Angle(deg) |  Angle between the left arm and the left forearm (in degrees) | float |
| Right_Arm_Angle(deg) |  Angle between the right arm and the left forearm (in degrees) | float |
| Left_Sh_Vel(deg/s) |  Angular velocity of the left shoulder-arm joint (in degrees per second) | float |
| Right_Sh_Vel(deg/s) |  Angular velocity of the right shoulder-arm joint (in degrees per second) | float |
| Left_Arm_Vel(deg/s) |  Angular velocity of the left arm-forearm joint (in degrees per second) | float |
| Right_Arm_Vel(deg/s) |  Angular velocity of the right arm-forearm joint (in degrees per second) | float |
| Left_Height_Angle(deg) |  Angle between the user's left shoulders and wrists (in degrees) | float |
| Right_Height_Angle(deg) |  Angle between the user's right shoulders and wrists (in degrees)  | float |

![System Description](img/opencv_arms.png?raw=true)


### Drum Vibration log (`drum_vibration_log.csv`)
| Colum Name  |      Description      |  Type |
|----------|:-------------:|------:|
| Index |  Index of each event | integer |
| Time(epoch ms) |  The PC epoch time when the event happen. (in milliseconds) | long |
| Z_Axis_Acceleration_(ms/s^2) | The vertical acceleration mesured by the accelerometer attached inside the taiko joystick | float |


### Hits, Timming and Joystick events log (`midi_hits_log.csv`)
| Colum Name  |      Description      |  Type |
|----------|:-------------:|------:|
| Index |  Index of each event | integer |
| Joystick Hit Time(epoch-ms) |  The PC epoch time when user press the taiko (in milliseconds) | long |
| Note Time(epoch-ms) |  The PC epoch time when MIDI note was played (in milliseconds) | long |
| Time Difference(ms) |  The user's reaction time to the MIDI note | long |
| Hit(bool) |  1 if it was a GOOD hit, 0 if MISS hit | boolean |

## Configuration
The program has many control paramters. The value of these constants can be modified inside the `include/globals.py` file. Or using the options panel.

![Options Panel](img/config_screenshot.png?raw=true)

- OP_MODELS_PATH - OpenPose models folder
- OP_PY_DEMO_PATH - OpenPose main path folder 
- CAM_OPCV_ID - Open CV camera ID  
- MAX_TXT_FRAMES - Number of frames the hit text will be displayed
- DRAW_SENSEI_ARMS - If true, draws the sensei's arms over the users shoulders
- DRAW_HITS - If true, draws visual feedback of good or bad hits, over the user's head.
- MIDI_MAX_PAST - Maximum time lapse before any MIDI note, to consider a past hit a GOOD hit (in milliseconds).
- MIDI_MAX_FUTURE - Maximum time lapse after any MIDI note, to consider a future hit GOOD hit (in milliseconds).
- MIDI_PLAY_GOOD_HITS - If true, plays the MIDI notes ONLY when the user's makes a 
GOOD hit.
- MIDI_PLAY_ALL_HITS - If true, plays a MIDI note all the times the user's press the joystick. 
- MIDI_PLAY_MIDIFILE_NOTES - If true, plays the instructor's MIDI file notes.  
- MIDI_MAX_ARM_VOL - Maximum MIDI volume value when the user's arms are at their highest (wrists up and over the head)
- MIDI_MIN_ARM_VOL - Minimum MIDI volume value when the user's arms are at their lowest (wrists infront of shoulders or chest)
- JOY_CNX_NUMBER - ID number of the joystick in pygame. 
- JOY_BUFF_SIZE = Size of joystick events buffer.


## How to Install
First you need to install Openpose for Python (from source code). 
For this you need to pre-install: 

(Different versions may also work)

- Git
    - https://git-scm.com/download/win
- CMake
    - https://cmake.org/
- Visual Studio 2019 
    - https://www.techspot.com/downloads/7241-visual-studio-2019.html (direct link)
- Python (3.7)
    - https://www.python.org/downloads/release/python-370/
- CUDA and cuDNN (OpenPose recommends CUDA 11 and cuDNN 8)
    - CUDA
    - https://developer.nvidia.com/cuda-toolkit-archive
    - cuDNN
    - https://developer.nvidia.com/rdp/cudnn-archive


Then follow the instructions mentioned in Openpose documentation:  
https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation/0_index.md#compiling-and-running-openpose-from-source 

Then install all the python libraries using pip:
- numpy 
    - `pip install numpy`
- opencv  
    - `pip install opencv-python`
- pygame  
    - `pip install pygame`
- mido
    - `pip install mido`
- pyserial 
    - `pip install pyserial`
- wxPython  
    - `pip install wxPython`
- rtmidi 
    - `pip install python-rtmidi`

