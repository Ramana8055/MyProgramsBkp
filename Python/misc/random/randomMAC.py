#!/usr/bin/python
from random import randint

def func(arg):
	return "%02X" % arg
def randMAC():
	mac=[
		randint(0,0xff),
		randint(0,0xff),
		randint(0,0xff),
		randint(0,0xff),
		randint(0,0xff),
		randint(0,0xff)
	]
	return ":".join(map(func,mac))

print randMAC()
	
