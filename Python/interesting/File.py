#!/usr/bin/python
from sys import argv
with open(argv[1],'r') as f:
    print f.tell()
    for line in f:
        print line  
    print f.tell()
    f.seek(0)
    print f.tell()
    for line in f:
        print line
