#!/usr/bin/python

from sys import exit,exc_info,stdout
from time import sleep

try:
	print "hello"
	#raise KeyboardInterrupt
	while True:
		print "hello"
		stdout.flush()
		sleep(1)

except KeyboardInterrupt:
	print "Key board Interrupt"
	stdout.flush()
	exit(0)
