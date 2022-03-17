import serial
import time
import os
import csv
import serial.tools.list_ports

from multiprocessing import Process, Value

class M5SerialCom:
    def __init__(self, bauds, joyForces, joyIndex, log_path):
        # Init serial
        self.baudrate = bauds
        self.port = self.getSerialPort()
        if self.port == None:  # If nothing is found use COM5 as a default port (to avoid program crash)
            self.port = 'COM5' 

        self.log_file = log_path + os.path.sep + 'drum_vibration_log.csv'
        self.ser = None
        self.lastMax = 0.0
        self.jIndex = joyIndex

        self.stopFlag = Value('b', False)
        self.serialProcess = Process(target=self.serialLoop, args=(self.stopFlag, joyForces)) 
        self.serialProcess.daemon = True 
        self.accLogBuff = []     # logged into disk when the tread is stopped
        self.LAST_MAX_LEN = 3
        self.JOYSTICK_MASS = 0.1   # 100 gr mass in kilograms to calculate Force from Acceleration

    # Init Serial port (COM)
    # Search for the M5 stick and connects it to the right COM port
    def getSerialPort(self):
        ports = serial.tools.list_ports.comports()
        # Serial ouput of a couple of M5SticksC
        # COM7: USB Serial Port (COM7) [USB VID:PID=0403:6001]
        # COM5: USB Serial Port (COM5) [USB VID:PID=0403:6001 SER=75523506B6A]
        for port, desc, hwid in sorted(ports):
            # print("{}: {} [{}]".format(port, desc, hwid))
            if "0403:6001" in hwid:
                return port

    # starts the thread 
    def start(self):
        self.stopFlag.value = True
        self.serialProcess.start()
    
    # stops the thread main cycle
    def stop(self):
        self.stopFlag.value = False

    # returns false if the M5stick is not connected
    def m5Check(self):
        if self.getSerialPort() is None:
            return False
        else:
            return True

    # when the thread is stopped log all captured data on disk
    # (must be called inside the thread process)
    def logOnDisk(self):
        with open(self.log_file, 'w', newline='', encoding='utf-8') as csvfile:
            wr = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            wr.writerow(['Index', 'Time(epoch)', 'Z_Axis_Acceleration_(ms/s^2)'])
            for i, line in enumerate(self.accLogBuff):
                acc_s = line[1].decode('utf-8')
                acc_z = acc_s.split(',')[1].split(',')[0]
                # f_y = float(acc_y) * self.JOYSTICK_MASS
                wr.writerow( [i, line[0], acc_z] )


    def getLastAccData(self):
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

        now = int(time.time_ns() / 1000000)
        readLine = self.ser.readline()
        self.accLogBuff.append( (now, readLine)  )
        fMax = 0
        while stopFlag.value:
            now = int(time.time_ns() / 1000000)
            readLine = ( self.ser.readline() )
            self.accLogBuff.append( (now, readLine)  )
            fMax = fMax + 1
            if fMax == self.LAST_MAX_LEN:
                joyForces[self.jIndex] = self.getLastAccData()
                fMax = 0
        self.logOnDisk()

        self.ser.close()
        
