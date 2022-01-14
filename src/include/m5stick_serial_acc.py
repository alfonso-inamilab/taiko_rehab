import serial
import time
import csv
from multiprocessing import Process, Value

class M5SerialCom:
    def __init__(self, bauds, port, joyForces, joyIndex, log_file):
        # Init serial
        self.baudrate = bauds
        self.port = port
        self.log_file = log_file
        self.ser = None
        self.lastMax = 0.0
        self.jIndex = joyIndex

        self.stopFlag = Value('b', False)
        self.serialProcess = Process(target=self.serialLoop, args=(self.stopFlag, joyForces))  
        self.accLogBuff = []     # logged into disk when the tread is stopped
        self.LAST_MAX_LEN = 3
        self.JOYSTICK_MASS = 0.1   # 100 gr mass in kilograms to calculate Force from Acceleration

    # starts the thread 
    def start(self):
        self.stopFlag.value = True
        self.serialProcess.start()
    
    # stops the thread main cycle
    def stop(self):
        self.stopFlag.value = False

    # when the thread is stopped log all captured data on disk
    # (must be called inside the thread process)
    def logOnDisk(self):
        with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            wr.writerow(['User_ID', 'Time_Lapse(ms)', 'Time(epoch)', 'Z_Axis_Accelration_(ms/s^2)', 'Force(N)'])
            first_event = 0
            for i, line in enumerate(self.accLogBuff):
                acc_s = line[1].decode('utf-8')
                acc_y = acc_s.split(',')[1].split(',')[0]
                f_y = float(acc_y) * self.JOYSTICK_MASS
                if i == 0:
                    first_event = line[0]
                wr.writerow( [0, line[0]-first_event, line[0], acc_y, f_y] )


    def getLastForce(self):
        acc_s = self.accLogBuff[-1][1].decode('utf-8')
        return float(acc_s.split(',')[1].split(',')[0])


    # serial comminication main loop
    # REMEMBER: This is an independet process, so the variables are NOT shared with the main thread. 
    def serialLoop(self, stopFlag, joyForces ):
        try:
            self.ser = serial.Serial(self.port, self.baudrate)
        except :
            print ("ERROR: Cannot open serial port " + str(self.port))
            return False

        now = int(time.time() * 1000)
        readLine = self.ser.readline()
        self.accLogBuff.append( (now, readLine)  )
        fMax = 0
        while stopFlag.value:
            now = int(time.time() * 1000)
            readLine = ( self.ser.readline() )
            self.accLogBuff.append( (now, readLine)  )
            fMax = fMax + 1
            if fMax == self.LAST_MAX_LEN:
                joyForces[self.jIndex] = self.getLastForce()
                fMax = 0
        self.logOnDisk()

        self.ser.close()
        
