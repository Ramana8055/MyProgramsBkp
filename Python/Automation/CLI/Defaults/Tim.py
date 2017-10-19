#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system,getcwd
from time import sleep

app		= "tim"
Timeout		= 100
passwd		= ""
exit_flag	= 0

#Configuration Start

streaming_ip	= "192.168.20.72"
streaming_port	= "51015"
certattach_rate	= "1000"

#Configuration End

def rev_comm(child):
	child.sendline("review")
	child.expect("#")
	child.sendline("commit")
	status=child.expect(["[Oo]peration","[fF]ailed","#",TIMEOUT,EOF])
	if status != 2:
		print "Commit failed"
		exit(1)
	child.sendline("review")
	child.expect("#")
	sleep(1)
	child.sendline("exit")
	child.expect("Savari>>")
	child.sendline("show system date")
	child.expect("Savari>>")
	child.sendline("config app "+app)
	child.expect("#")

def Usage():
	global exit_flag
	exit_flag = 1
	print "Usage:"
	print "\t",argv[0],"<board ip> <streaming_mode(send/receive/disable)>"
	exit(1)
	

#***********************************START******************************************#
try:
	if len(argv)!=3:
		Usage()

	ip	= argv[1]
	mode	= argv[2]

	if mode != "send" and mode != "receive" and mode != "disable":
		print "Invalid mode",mode
		Usage()

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
	status=child.expect(["Savari>>",TIMEOUT,EOF])
	if status!=0:
		print "[",status,"]","Didn't enter CLI"
		exit_flag = 1
		exit(1)

	child.sendline("config app "+app)
	status=child.expect(["[cC]ommand","[iI]nvalid","#",TIMEOUT,EOF])
	if status!=2:
		print "Invalid command"
		exit_flag = 1
		exit(1)

	child.sendline("enable")
	child.expect("#")

	if mode == "send":
		child.sendline("streaming mode enable send")
	elif mode == "receive":
		child.sendline("streaming mode enable receive")
	else:
		child.sendline("streaming mode disable")
	child.expect("#")

	child.sendline("streaming ipaddr "+streaming_ip)
	child.expect("#")

	child.sendline("streaming port "+str(streaming_port))
	child.expect("#")

	child.sendline("security certificate-attachrate "+str(certattach_rate))
	child.expect("#")

	rev_comm(child)

	exit(0)

except KeyboardInterrupt:
	exit(0)
except SystemExit:
	if not exit_flag:
		system("cat TimStatus.txt | grep -A1 -B2 -Ei 'failed|invalid|\^command|parameter|timedout' > TimError.txt")
		system("if [ `cat TimError.txt|wc -l` -eq 0 ] ; then rm TimError.txt ; fi")
		exit(1)
	else:
		exit(0)
except:
	print "Exception",exc_info()
	system("cat TimStatus.txt | grep -A1 -B2 -Ei 'failed|invalid|\^command|parameter|timedout' > TimError.txt")
	system("if [ `cat TimError.txt|wc -l` -eq 0 ] ; then rm TimError.txt ; fi")
	exit(1)
