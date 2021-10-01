# -*-coding:utf-8-*-

import sys
from socket import *
import time

"""
IPアドレスの確認方法
コマンドプロンプトで「ipconfig」と入力し
と入力し、
［IPv4 アドレス］または［IPアドレス］の値が、使用しているパソコンのIPアドレスです。
"""

print("start network")
addr = ('', 50007)

print("network setup started")
UDPSock = socket(AF_INET, SOCK_DGRAM)
UDPSock.settimeout(0.0001)
print("Connected !!")
print("Network info -->" + str(addr))
UDPSock.bind(addr) 


print("setup finished")

while True:
    try:
        (data, addr) = UDPSock.recvfrom(1024)
    except timeout:
        continue

    if addr !=0:
        str_data = data.decode('utf-8')
        print(f"get message from {addr} --> {str_data}")

print("end!")