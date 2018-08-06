#!/usr/bin/python
from sys import exit,stdout,exc_info

try:
    print sum(1 for line in open("MyFile"))
except IOError:
    print "Failed to open"
except:
    print exc_info()
