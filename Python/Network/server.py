#!/usr/bin/python3
import socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
host=socket.gethostname()
port=60000
s.bind((host,port))
s.listen(5)
while True:
   c, addr = s.accept()    
   print("Host name:",addr)
   c.send("Thank you for connecting".encode())
   c.close()               	
