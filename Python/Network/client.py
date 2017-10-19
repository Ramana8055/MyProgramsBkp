#!/usr/bin/python3
import socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
host=socket.gethostname()
port=60000
s.connect((host,port))
print(s.recv(1024).decode())
s.close
