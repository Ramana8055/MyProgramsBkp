#!/usr/bin/python -B
from sys import stdout,exit,exc_info

try:	
	fd=open("MyFile",'rb')
except:
	print exc_info()
	exit(1)

print "File \"",fd.name,"\" is opened"

for i in range(5):
	try:
		print fd.next(),
	except StopIteration:
		print "EOF reached!! No more lines"
		exit(1)
