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
        self.accLogBuff = []      
        self.MAX_BUF_LEN = 500
        self.LAST_MAX_LEN = 3
        self.JOYSTICK_MASS = 0.1   # 100 gr 

    # starts the thread 
    def start(self):
        self.stopFlag.value = True
        self.serialProcess.start()
    
    # stops the thread main cycle
    def stop(self):
        self.stopFlag.value = False

    # save the captured lines into a file
    def logOnDisk(self):
        with open(self.log_file, 'w', newline='') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for i, line in enumerate(self.accLogBuff):
                acc_s = line[1].decode('utf-8')
                
                acc_y = acc_s.split(',')[1].split(',')[0]
                wr.writerow( [line[0], acc_y] )

    # log the Last Max Force value (in a given range LAST_MAX_LEN)
    def getLastForce(self):
        # accLen = len(self.accLogBuff)
        # self.lastMax = 0
        # for i in range(accLen-1, accLen-self.LAST_MAX_LEN, -1):
        #     acc_s = self.accLogBuff[i][1].decode('utf-8')
        #     acc_y = float(acc_s.split(',')[1].split(',')[0])
        #     if (self.lastMax < acc_y):
        #         self.lastMax = acc_y
        # return self.lastMax * self.JOYSTICK_MASS
        acc_s = self.accLogBuff[-1][1].decode('utf-8')
        return float(acc_s.split(',')[1].split(',')[0])


    # serial comminication main loop
    def serialLoop(self, stopFlag, joyForces ):
        try:
            self.ser = serial.Serial(self.port, self.baudrate)
        except :
            print ("ERROR: Cannot open serial port " + str(self.port))
            return False

        now = int(time.time() * 1000)
        readLine = self.ser.readline()
        self.accLogBuff.append( (now, readLine)  )
        bufLen = 0
        fMax = 0
        while stopFlag.value:
            now = int(time.time() * 1000)
            readLine = ( self.ser.readline() )
            self.accLogBuff.append( (now, readLine)  )
            bufLen = bufLen + 1
            fMax = fMax + 1
            if bufLen == self.MAX_BUF_LEN:
                self.logOnDisk()
                bufLen = 0
            if fMax == self.LAST_MAX_LEN:
                joyForces[self.jIndex] = self.getLastForce()
                fMax = 0

        self.ser.close()
        
