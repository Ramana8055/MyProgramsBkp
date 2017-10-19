#!/usr/bin/python -B
# The -B option suppresses .pyc files from being generated.
import sys
from func import sum
try:
	try:
		a=int(raw_input("Enter first number:")) #raw_input is similar to scanf which takes input in the form of strings
		b=int(raw_input("Enter second number:"))
	except ValueError,err:
		print err
		sys.exit(1)
	#except:
	#	print sys.exc_info() #Use this function to print error and know the exception if it is not known
	#	sys.exit(1)
	c=sum(a,b)
	print c
except KeyboardInterrupt:
	print "",
