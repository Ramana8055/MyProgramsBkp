#!/usr/bin/python -B
import sys
import thread
a=0
def increment(i):
	global a
	while True:
		a+=1
		print i,a
def decrement(i):
	global a
	while True:
		a-=1
		print i,a
try:
	thread.start_new_thread(increment,("thread1",))
	thread.start_new_thread(decrement,("thread2",))
except Exception, err:
	print "Thread creation Failed!!",err
	sys.exit(1)

while 1:
	pass
