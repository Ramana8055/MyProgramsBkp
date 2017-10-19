#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system,getcwd
from random import randint,getrandbits
from time import time,sleep
from socket import inet_ntoa
from struct import pack
from netaddr.ip import IPAddress

app		= "store-repeat"
Timeout		= 100
passwd		= ""
exit_flag	= 0
privileged	= False
toggle		= True

def rev_comm(child):
	child.sendline("review")
	child.expect("#")
	child.sendline("commit")
	status=child.expect(["[Oo]peration","[fF]ailed","#",TIMEOUT,EOF])
	if status!=2:
		print "Commit failed"
		exit(1)
	child.sendline("review")
	child.expect("#")
	sleep(1)
	child.sendline("exit")
	child.expect(">")
	child.sendline("show system date")
	child.expect(">")
	child.sendline("config app "+app)
	child.expect("#")
	
def check_all_ports(child):
	global toggle
	for port in range(1,65536):
			toggle = not toggle
			child.sendline("streaming port "+str(port))
			child.expect("#")
			if toggle:
				child.sendline("streaming ip "+inet_ntoa(pack('>I',randint(0,0xffffffff))))
			else:
				child.sendline("streaming ip "+str(IPAddress(getrandbits(128))))
			child.expect("#")
			for i in range(-500,5001):
				child.sendline("security certificate-attachrate "+str(i))
				child.expect("#")
				rev_comm(child)

#***********************************START******************************************#
try:
	if len(argv)!=2:
		exit_flag = 1
		print "Usage:"
		print "\t",argv[0],"<board ip>"
		exit(1)

	ip=argv[1]
	system("rm -rf ~/.ssh/known_hosts")

	try:
		child=spawn("ssh -p51012 root@"+ip)
	except:
		print "ssh failed",exc_info()
		exit_flag = 1
		exit(1)

	child.logfile_read=open("TimStatus.txt",'wb')
	child.timeout=Timeout

	while True:
		status=child.expect(["[pP]assword","[yY]es/[nN]o","[yY]/[nN]","[cC]onnection",\
							"[Nn]o [rR]oute",TIMEOUT,EOF])
		if status==0:
			child.sendline("")
			break
		elif status==1:
			child.sendline("yes")
			continue
		elif status==2:
			child.sendline("y")
			continue
		else:
			print "Connection Failed"
			exit_flag = 1
			exit(1)

	status=child.expect(["root@*","[pP]ermission","[wW]rong","[iI]nvalid",TIMEOUT,EOF])
	if status!=0:
		print "[",status,"]","Invalid Password or Timed Out"
		exit_flag = 1
		exit(1)

	child.sendline("sav_cmd")
	status=child.expect([">",TIMEOUT,EOF])
	if status!=0:
		print "[",status,"]","Didn't enter CLI"
		exit_flag = 1
		exit(1)

	if privileged:
		child.sendline("enable privileged-mode")
		child.expect("[eE]nter [pP]assword")
		child.sendline("6efre#ESpe")
		child.expect("\+")

	child.sendline("config app "+app)
	status=child.expect(["[cC]ommand","[iI]nvalid","#",TIMEOUT,EOF])
	if status!=2:
		print "Invalid command"
		exit(1)

	child.sendline("enable")
	child.expect("#")
	rev_comm(child)

	child.sendline("streaming mode enable send")
	child.expect("#")
	rev_comm(child)

	child.sendline("streaming port 1024")
	child.expect("#")
	rev_comm(child)

	child.sendline("streaming ip 192.168.20.168")
	child.expect("#")
	rev_comm(child)

	check_all_ports(child)	

	child.sendline("streaming mode enable receive")
	child.expect("#")
	rev_comm(child)

	check_all_ports(child)

	child.sendline("streaming mode disable")
	child.expect("#")
	rev_comm(child)
	
	check_all_ports(child)

except KeyboardInterrupt:
	system("cat TimStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > TimError.txt")
	system("if [ `cat TimError.txt | wc -l` -eq 0 ] ; then rm TimError.txt ; fi")
	exit(0)
except SystemExit:
	if not exit_flag:
		system("cat TimStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > TimError.txt")
		system("if [ `cat TimError.txt | wc -l` -eq 0 ] ; then rm TimError.txt ; fi")
		exit(0)
	else:
		exit(1)
except:
	print "Exception",exc_info()
	system("cat TimStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > TimError.txt")
	system("if [ `cat TimError.txt | wc -l` -eq 0 ] ; then rm TimError.txt ; fi")
	exit(1)
