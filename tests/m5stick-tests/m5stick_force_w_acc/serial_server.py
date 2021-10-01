import serial
import time
from threading import Thread

class M5SerialCom:
    def __init__(self, bauds=115200, port='COM3' ):
        # Init serial
        self.ser = serial.Serial()
        self.ser.baudrate = bauds
        self.ser.port = port

        self.serialThread = Thread(target=self.serialLoop, args=( ))
        self.serialThread.daemon = True
        self.run = False

    # starts the thread 
    def start(self):
        self.run = True
        self.ser.open()
        self.serialThread.start() 
    
    # stops the thread main cycle
    def stop(self):
        self.run = False
        self.ser.close()

    # serial comminication main loop
    def serialLoop(self):
        try:
            while self.run:
                readLine = self.ser.readline()
                print (readLine)
        finally:
            self.stop()

def main():
    serial = M5SerialCom()
    serial.start()
    while True:
        try:
            time.sleep(10)
        except KeyboardInterrupt :
            serial.stop()
            break


if __name__ == "__main__":
    main()