#!/usr/bin/python -B
import socket
import struct
import random

print socket.inet_ntoa(struct.pack('>I',random.randint(0,0xffffffff)))
