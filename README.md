# Taiko Rehab
Cognitive and physical rehabilitation system for old people by playing Taiko

## System description
Taiko Rehab uses a MIDI file and a video file of an instructor playing the Taiko. When the music starts, Taiko Rehab plays the MIDI and video file together, while the system registers the user's shoulders and arms positions, the hitting timming and the force. Finally when the program is closed, all the data is dumped into a CSV file for later analysis. 

![System Description](img/system_description.png?raw=true)

## Usage 

First it is necessary to pre-process the video file of the instructor to create a CSV file that saves the instructors arm and shoulders positions. 
To do it, open a terminal in the same folder whre the TaikoRehab is located and type:

`python taiko_rehab.py -p [INSTRUCTOR VIDEO FILE.mp4]`

Wait until the video is played completely and the program closes it self. 

To use TaikoRehab, open a terminal and type the following command:

`python taiko_rehab.py [MUSIC MIDI FILE .midi] [INSTRUCTOR VIDEO FILE.mp4]`

(NOTE. The instructor video file and the CSV file must be in the same folder and have the same name)

## Hardware

The sensor used for this are: 
- Taiko joystick to measure hit timming 
https://www.amazon.co.jp/gp/product/B07T9DZBW9
- Accelerometer to measure hit force (MPU6050 attached to Taiko Joystick)
 https://www.amazon.co.jp/-/en/gp/product/B07MPBMRWD/ref=ox_sc_act_title_1?smid=A3ALF3N55UI5NK&psc=1
- Web Camera to measure the wrist position with OpenPose


## Event Log Description 

| Colum   |      Description      |  Type |
|----------|:-------------:|------:|
| User_ID |  Number to identify each user (for future multiplayer version) | integer |
| Time(epoch) | The PC epoch time when the event happen. (in milliseconds) | long |
| Z_Axis_Accelration_(ms/s^2) | Acceleration on Z axis of the taiko surface | float |
| Force(N) | Approximation of the hitting force (acc in z axis * sensor mass) (given in Newton) | float |
| Left_Arm_Angle | The angle between the left arm and forearm | float |
| Right_Arm_Angle | The angle between the right arm and forearm | float |
| Left_Shoulder_Angle | The angle between the left arm and shoulder | float |
| Right_Shoulder_Angle | The angle between the right arm and shoulder | float |
| Left_Arm_Angular_Vel | Left arm angular velocity (deg/sec) | float |
| Right_Arm_Angular_Vel | Right arm angular velocity (deg/sec) | float |
| Left_Shoulder_Angular_Vel | Left shoulder angular velocity (deg/sec) | float |
| Right_Shoulder_Angular_Vel | Right shoulder angular velocity (deg/sec) | float |
| Hit_Time(epoch) | PC epoch time when the user hit the taiko (in milliseconds) | long |
| Timming | Time difference between the event epoch and the hit epoch time (in ms) | long |
| Hit | HIT if the user hit the note, MISS if not | string |

## Configuration
The program has many control paramters. The value of these constants can be modified inside the `include/control_params.py` file. 

- OP_MODELS_PATH - OpenPose models folder
- OP_PY_DEMO_PATH - OpenPose main path folder 
- CAM_OPCV_ID - Open CV camera ID  
- MAX_TXT_FRAMES - Number of frames the hit text will be displayed
- MAX_NUM_PEOPLE - Number of users detected with OpenCV. -1 for No limit
- JOYSTICK_MASS - Mass of the sensor to calculate Force from Acceleration (in kilograms)
- MAX_PAST - Time difference between the hit a the note (in milliseconds) to consider a past hit OK
- MAX_FUTURE - Time difference between the hit a the note (in milliseconds) to consider a delayed hit OK

## Install
TODO. Make a better documentation

OpenPose, M5Stick libraries and several Python libraries must be installed in order for the system to correctly work. 