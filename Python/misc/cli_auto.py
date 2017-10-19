#!/usr/bin/python -B
from os import getcwd,system
from sys import stdout,exit,exc_info
from pexpect import *
from time import time,sleep
from random import randint
from socket import inet_ntoa
from struct import pack

enable=[
        {"send":{"type":"NULL"}},
	{"receive":{"type":"NULL"}}
]
mode=[
       {"enable":{"type":"non-edge",
		  "option":enable}
       },
       {"disable":{"type":"NULL"}}
]
streaming=[
	    {"mode":{"type":"non-edge",
		     "option":mode}
            },
	    {"ip":{"type":"edge",
		   "option":inet_ntoa(pack('>I',randint(0,0xffffffff)))}
            },
	    {"port":{"type":"edge",
		     "option":str(randint(1,65536))}
            }
]
tim=[
	{"enable":{"type":"NULL"}},
	{"streaming":{"type":"non-edge",
		      "option":streaming}
	},
	{"security":{"type":"edge",
		     "option":"certificate-attachrate "+str(randint(500,5000))}
        }
]
def all_cases(base,l,x):
	for i in base:
		for j in i:
			if i[j]["type"]=="edge":
				l.append(x+" "+j+" "+i[j]["option"])
			if i[j]["type"]=="non-edge":
				all_cases(i[j]["option"],l,(x+" "+j))
			if i[j]["type"]=="NULL":
				l.append(x+" "+j)
def get_tim():
	l=[]
	for i in tim:
		for j in i:
			if i[j]["type"]=="edge":
				l.append(j+" "+i[j]["option"])
			elif i[j]["type"]=="non-edge":
				all_cases(i[j]["option"],l,j)
			else:
				l.append(j)
	return l

#l=get_tim()
#for i in l:
#	print i
system("rm -rf ~/.ssh/known*")
try:
	child=spawn("ssh -p51012 root@192.168.20.213")
except:
	print "ssh failed"
	exit(1)
child.logfile=stdout
child.timeout=100
while True:
	status=child.expect(["[pP]assword","[yY]es/[nN]o","[yY]/[nN]","[nN]o [rR]oute","[cC]onnection",TIMEOUT,EOF])
	if status==0:
		child.sendline("")
		break
	elif status==1:
		child.sendline("yes")
		continue
	elif status==2:
		child.sendline("y")
		continue
	elif status==3:
		print "connection timed out"
		exit(1)
	elif status==4:
		print "No route to host"
		exit(1)
	else:
		print "Timed out"
		exit(1)

status=child.expect(["[pP]ermission","[tT]ry [aA]gain","[wW]rong","",TIMEOUT,EOF])
if status<=2:
	print "Invalid Password"
	exit(1)
elif status>3:
	print "Timed out"
	exit(1)
child.sendline("sav_cmd")
child.expect(">")#add failure case
child.sendline("config app tim")
child.expect(">")#add failure case
l=get_tim()
for line in l:
	child.sendline(line)
 	status=child.expect(["[cC]ommand","[iI]navlid","[pP]arameter","#",TIMEOUT,EOF])
	if status<=2:
		print "Failed"
	elif status>3:
		print "Timed out"
		exit(1)
	child.sendline("review")
	child.expect("#")#add failure case
	child.sendline("commit")
	child.expect("#") #failed(app,read,write)
