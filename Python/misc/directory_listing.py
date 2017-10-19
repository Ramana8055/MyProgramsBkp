#!/usr/bin/python
import os
import sys

print os.listdir(".")


#print only the files and leave directories

#print next(os.walk("."))[2]
print next(os.walk("."))[1]
