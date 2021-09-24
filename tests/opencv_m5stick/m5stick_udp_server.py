import sys
from socket import *
import time
from threading import Thread

# This class gets the accelration from a M5Stick using UDP. 
# It also has functions to log the data, calculate the velocity and saved the data in a file. 
class M5StickUDP:
    def __init__(self, port, dt, buffer_size, log_file):
        print("start network") 
        addr = ("", 50007)  # 192.168.0.9

        print("Network Setup started")
        self.UDPSock = socket (AF_INET, SOCK_DGRAM)
        self.UDPSock.settimeout(0.0001)
        print("Connected !!")
        print("Network info -->" + str(addr))
        self.UDPSock.bind(addr) 
        print("Network Setup finished")
        
        self.run = False
        self.udpThread = Thread(target=self.UDPLoop, args=())
        self.udpThread.daemon = True

        self.dt = dt   # dt must be given in milliseconds
        self.buffer_size = buffer_size
        self.accIndx = -1
        self.accBuff = [None] * buffer_size
        self.velIndx = -1
        self.velBuff = [None] * buffer_size

    # logs the accelration to save it in a csv file when full
    def logAccel(self,accx, accy, accz):
        self.accIndx = self.accIndx + 1
        if self.accIndx >= self.buffer_size:
            self.accIndx = 0

        self.accBuff[self.accIndx] = (accx, accy, accz)
    
    # logs the velocity to save it in a csv file when full
    def logVel(self, vel):
        self.velIndx = self.velIndx + 1
        if self.velIndx >= self.buffer_size:
            self.velIndx = 0
            # if self.log_file is not None:
                # self.saveCSV()

        self.velBuff[self.velIndx] = vel

    # return the last logged velocity
    def getM5Vel(self):
        return self.velBuff[self.velIndx]

    # returns the last logged accelaration
    def getM5Acc(self):
        return self.accBuff[self.accIndx]

    # returns the maximum value from the logged velocities
    # NOT TESTED YET
    def getPastMaxVel(self, axis, past_steps):
        indx = self.velIndx 
        maxVel = 0; steps - 0; 

        while (steps < past_steps): 
            if velBuff[indx][axis] > maxVel:
                maxVel = velBuff[indx][axis]
            steps = steps + 1

            indx=indx-1
            if indx < 0:
                indx = self.buffer_size

    # calculates the instant velocity 
    def calcM5Vel(self):
        past_acc = None; 
        if self.accIndx > 0:
            past_acc = self.accBuff[self.accIndx -1]
        else:
            past_acc = self.accBuff[0]
        now_acc = self.getM5Acc()

        vx = (now_acc[0] - past_acc[0]) / self.dt
        vy = (now_acc[1] - past_acc[1]) / self.dt
        vz = (now_acc[2] - past_acc[2]) / self.dt

        # print("Velocity       X:{2:4f}, Y:{2:4f}, Z:{2:4f}".format(vx, vy, vz) )  # DEBUG
        # print ("{2:4f},{2:4f},{2:4f}".format(vx,vy,vz))
        return (vx, vy, vz)

    # find a string between two characters
    def find_between(self, s, start, end):
        return (s.split(start))[1].split(end)[0]

    # starts the thread 
    def start(self):
        self.run = True
        self.udpThread.start() 
    
    # stops the thread main cycle
    def stop(self):
        self.run = False

    # main thread cycle 
    def UDPLoop(self):
        # now = 0;  past = 0
        while self.run:
            try:
                (data, addr) = self.UDPSock.recvfrom(1024)
            except timeout:
                continue

            if addr !=0:
                str_data = data.decode('utf-8')
                
                # parse accelration and cast the information 
                str_x = self.find_between(str_data,'x','x')
                str_y = self.find_between(str_data,'y','y')
                str_z = self.find_between(str_data,'z','z')

                # cast and log the accelration
                acc_x  = float(str_x);  acc_y  = float(str_y); acc_z = float(str_z)
                self.logAccel(acc_x, acc_y, acc_z) 

                # measure cycle time lapse (dt)
                # now = int( round(time.time() * 1000 ))
                # dt = now - past
                # past = now
                # print (dt)   # DEBUG

                vel = self.calcM5Vel()
                self.logVel(vel)
                # print("Acceleration       X:{2:4f}, Y:{2:4f}, Z:{2:4f}".format(acc_x, acc_y, acc_z) )  # DEBUG
                # print ("{2:4f},{2:4f},{2:4f}".format(acc_x,acc_y,acc_z))  # DEBUG


