#!/usr/bin/python
from socket import socket,AF_INET,SOCK_STREAM
from sys import argv,exit
from random import SystemRandom
from string import ascii_uppercase,ascii_lowercase,digits

if len(argv) != 2:
	print argv[0],"<board ip>"
	exit(1)

s=socket(AF_INET,SOCK_STREAM,0)
s.connect((argv[1],9999))

while True:
	s.send(''.join(SystemRandom().choice(ascii_uppercase + ascii_lowercase + digits) for _ in range(300) ))
s.close()
