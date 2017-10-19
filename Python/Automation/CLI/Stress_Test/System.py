#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system
from random import SystemRandom,randint,getrandbits
from struct import pack
from netaddr import IPAddress
from string import ascii_uppercase,ascii_lowercase,digits

exit_flag	= 0
Timeout		= 300
Passwd		= ""
toggle		= True
sshcmd		= "ssh -p51012 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"

def Usage():
	global exit_flag
	exit_flag=1
	print "Usage:"
	print "\t",argv[0],"<board-ip>"
	exit(1)

def check_status(child):
	status = child.expect(["[oO]peration","[Cc]onnection [Aa]ttempt","[Ww]rite [fF]ailed",\
			"[rR]ead [fF]ailed",">","#",TIMEOUT,EOF])
	if status >=6:
		print("Connection TimedOut or EOF reached")
		exit(1)
def configure_and_review_acl(child):
	child.sendline("show system acl list all")
	child.expect(">")

def configure_and_review_firewall(child):
	child.sendline("config system firewall list")
	child.expect(">")

def configure_and_review_syslogs(child):
	child.sendline("config system syslog")
	child.expect("#")

	child.sendline("enable")
	child.expect("#")
	
	child.sendline("size "+str(randint(-100,2500)))
	child.expect("#")

	child.sendline("loglevel "+str(randint(-100,20)))
	child.expect("#")

	child.sendline("time "+str(randint(-100,2880)))
	child.expect("#")

	child.sendline("disc_capacity "+str(randint(-100,200)))
	child.expect("#")

	child.sendline("commit")
	check_status(child)

	child.sendline("review")
	child.expect("#")

	child.sendline("exit")
	child.expect(">")

	child.sendline("show system syslog all")
	child.expect(">")

def configure_and_review_pcaplogs(child):
	child.sendline("config system pcaplog")
	child.expect("#")

	child.sendline("enable")
	child.expect("#")

	child.sendline("ethernet filesize "+str(randint(-100,2000)))
	child.expect("#")

	child.sendline("ethernet timeout "+str(randint(-100,500000)))
	child.expect("#")

	child.sendline("ethernet outcapture 1")
	child.expect("#")

	child.sendline("ethernet incapture 1")
	child.expect("#")

	child.sendline("dsrc0 filesize "+str(randint(-100,2000)))
	child.expect("#")

	child.sendline("dsrc0 timeout "+str(randint(-100,500000)))
	child.expect("#")

	child.sendline("dsrc0 outcapture 1")
	child.expect("#")

	child.sendline("dsrc0 incapture 1")
	child.expect("#")
	
	child.sendline("dsrc1 filesize "+str(randint(-100,2000)))
	child.expect("#")

	child.sendline("dsrc1 timeout "+str(randint(-100,500000)))
	child.expect("#")

	child.sendline("dsrc1 outcapture 1")
	child.expect("#")

	child.sendline("dsrc1 incapture 1")
	child.expect("#")

	child.sendline("commit")	
	check_status(child)

	child.sendline("review")
	child.expect("#")

	child.sendline("exit")
	child.expect(">")

def configure_and_review_settings(child):
	global toggle
	toggle=not toggle  #Date and hwclock are to be configured
	if toggle:	
		child.sendline("config system hwclock systohc")
	else:
		child.sendline("config system hwclock hctosys")
	child.expect(">")

	child.sendline("show system date")
	child.expect(">")
	child.sendline("show system hwclock")
	child.expect(">")

	hostname="".join(SystemRandom().choice(ascii_uppercase+ascii_lowercase+digits) for _ in range(64))
	child.sendline("config system settings hostname "+hostname)
	child.expect(">")

	child.sendline("config system settings commit")
	check_status(child)

	child.sendline("config system settings review")
	child.expect(">")

	child.sendline("show system cpu-usage")
	child.expect(">")
	
	child.sendline("show system memory-usage")
	child.expect(">")

	child.sendline("show system uptime")
	child.expect(">")

	child.sendline("show system disk-usage")
	child.expect(">")

def review_network(child):
	child.sendline("config system network eth0 proto dhcp")
	child.expect(">")

	child.sendline("config system network eth0 commit")
	check_status(child)

	child.sendline("config system network eth0 review")
	child.expect(">")

	child.sendline("config system network dsrc0 review")
	child.expect(">")

	child.sendline("config system network dsrc1 review")
	child.expect(">")

	child.sendline("show system network eth0 stats")
	child.expect(">")

	child.sendline("show system network dsrc0 stats")
	child.expect(">")

	child.sendline("show system network dsrc1 stats")
	child.expect(">")

	child.sendline("show system network eth0 all")
	child.expect(">")	

	child.sendline("show system network dsrc0 all")
	child.expect(">")	

	child.sendline("show system network dsrc1 all")
	child.expect(">")	

try:

	if len(argv)!=2:
		Usage()

	ip=argv[1]
	try:
		child=spawn( sshcmd+ip)
	except:
		print "ssh failed",exc_info()
		exit_flag = 1
		exit(1)
	child.logfile_read=open("SystemStatus.txt",'w')
	child.timeout=Timeout

	while True:
		status=child.expect(["[pP]assword","[yY]es/[nN]o","[yY]/[nN]","[cC]onnection",\
                                                        "[Nn]o [rR]oute",TIMEOUT,EOF])
                if status==0:
                        child.sendline(Passwd)
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
                print "[",status,"]","Couldn't enter CLI"
		exit_flag = 1
                exit(1)

	while True:
		configure_and_review_settings(child)
		review_network(child)
		configure_and_review_firewall(child)
		configure_and_review_acl(child)
		configure_and_review_syslogs(child)
		configure_and_review_pcaplogs(child)

	exit(0)
	
except KeyboardInterrupt:
	system("cat SystemStatus.txt | grep -A1 -B3 -Ei 'timedout|failed|invalid|\^command|parameter' > SystemErrors.txt")
	system("if [ `cat SystemError.txt|wc -l` -eq 0 ] ; then rm SystemError.txt ; fi")
	exit(0)
except SystemExit:
	if not exit_flag:
		system("cat SystemStatus.txt | grep -A1 -B3 -Ei 'timedout|failed|invalid|\^command|parameter' > SystemErrors.txt")
		system("if [ `cat SystemError.txt|wc -l` -eq 0 ] ; then rm SystemError.txt ; fi")
		exit(0)
	else:
		exit(1)
except (TIMEOUT,EOF):
	system("cat SystemStatus.txt | grep -A1 -B3 -Ei 'timedout|failed|invalid|\^command|parameter' > SystemErrors.txt")
	system("if [ `cat SystemError.txt|wc -l` -eq 0 ] ; then rm SystemError.txt ; fi")
	print("Network is down")
	exit(1)
except:
	print "Global Exception",exc_info()
	system("cat SystemStatus.txt | grep -A1 -B3 -Ei 'timedout|failed|invalid|\^command|parameter' > SystemErrors.txt")
	system("if [ `cat SystemError.txt|wc -l` -eq 0 ] ; then rm SystemError.txt ; fi")
	exit(1)
