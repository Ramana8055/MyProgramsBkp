#!/usr/bin/python -B 
import sys
import os
import pexpect
from base import *

fin=['{0} {1} {2} {3} {4}'.format(i,j,k,l,m) for i in main_list for j in config_list
		 for k in config_app for l in config_dp for m in interface
	 	 if (i=="config" and j=="app" and k=="dsrcproxy" and l=="ifname") ]

for x in fin:
	print x
