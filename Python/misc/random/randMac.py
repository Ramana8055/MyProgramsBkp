#!/usr/bin/python

import random
#
def randomMAC():
	mac = [ 
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff) ]
	return ':'.join(map(lambda x: "%02x" % x, mac))
#
print randomMAC()
