# -*-coding:utf-8-*-

import sys
from socket import *
import time

def find_between(s, start, end):
    return (s.split(start))[1].split(end)[0]

def main():
    print("start network")
    addr = ("", 50007)  # 192.168.0.9

    print("network setup started")
    UDPSock = socket (AF_INET, SOCK_DGRAM)
    UDPSock.settimeout(0.0001)
    print("Connected !!")
    print("Network info -->" + str(addr))
    UDPSock.bind(addr) 

    print("setup finished")

    while True:
        try:
            (data, addr) = UDPSock.recvfrom(2048)
        except timeout:
            continue

        if addr !=0:
            str_data = data.decode('utf-8')
            
            # parse and cast the information 
            str_x = find_between(str_data,'x','x')
            str_y = find_between(str_data,'y','y')
            str_z = find_between(str_data,'z','z')

            acc_x  = float(str_x);  acc_y  = float(str_y);  acc_z  = float(str_z); 
            print("Acceleration       X:{2:4f}, Y:{2:4f}, Z:{2:4f}".format(acc_x, acc_y, acc_z) )  # DEBUG

if __name__ == '__main__':
    main()