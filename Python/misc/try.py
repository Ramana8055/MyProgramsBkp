#!/usr/bin/python -B
import sys
import os

list1=["config","show","enable"]
list2=["app","system"]
list3=["dsrcproxy","ipv6","gps"]


a=[(i,x,y) for i in list1 for x in list2 for y in list3]
#print a


for elem in a:
	for x in elem:
		print x,
	print ""


