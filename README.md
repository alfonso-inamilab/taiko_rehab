# Taiko Rehab
Cognitive and physical rehabilitation system with cooperative taiko playing

## System description
Taiko Rehab can play any MIDI file while automatically record the users' movement, wrist height and hitting timming and force. All this data then is dumped into a CSV for later analysis.  

The sensor used for this are: 
- Taiko joystick to measure hit timming 
https://www.amazon.co.jp/gp/product/B07T9DZBW9
- Accelerometer to measure hit force (MPU6050 attached to Taiko Joystick)
 https://www.amazon.co.jp/-/en/gp/product/B07MPBMRWD/ref=ox_sc_act_title_1?smid=A3ALF3N55UI5NK&psc=1
- Web Camera to measure the wrist position with OpenPose

![System Description](img/system_description.png?raw=true)

## Event Log Description 

| Colum   |      Description      |  Type |
|----------|:-------------:|------:|
| User_ID |  Number to identify each user (for future multiplayer version) | integer |
| Time(epoch) | The PC epoch time when the event happen. (in milliseconds) | long |
| Z_Axis_Accelration_(ms/s^2) | Acceleration on Z axis of the taiko surface | float |
| Force(N) | Approximation of the hitting force (acc in z axis * sensor mass) (given in Newton) | float |
| Left_Height(Norm) | Normalized left wrist height. (normalized to the camera Y resolution) | float |
| Right_Height(Norm) | Normalized right wrist height. (normalized to the camera Y resolution) | float |
| Left_Height(Raw) | Raw OpenPose left wrist height position | float |
| Right_Height(Raw) | Raw OpenPose right wrist height position | float |
| Hit_Time(epoch) | PC epoch time when the user hit the taiko (in milliseconds) | long |
| Timming | Time difference between the event epoch and the hit epoch time (in ms) | long |
| Hit | HIT if the user hit the note, MISS if not | string |

## Usage 
Open a terminal where the progra is located and type:

`python taiko_rehab.py [midi_file_path.mid]`

## Configuration
The program has many constant to control several paramters. These constants are in capital letters placed on the top of each Python file. 

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