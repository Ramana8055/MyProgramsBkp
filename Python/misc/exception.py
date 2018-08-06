#!/usr/bin/python
from sys import exc_info,exit

a=10
b=0

try:
    c=a/b

#except ZeroDivisionError:
#   pass
except:
    print exc_info()[0]

