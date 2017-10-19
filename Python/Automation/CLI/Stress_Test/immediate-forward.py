#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system
from struct import pack
from random import randint,getrandbits
from time import time,sleep
from socket import inet_ntoa
from netaddr.ip import IPAddress,IPNetwork

app		= "immediate-forward"
Timeout		= 100
passwd		= ""
exit_flag	= 0

def rev_comm(child):
        child.sendline("review")
        child.expect("#")
        child.sendline("commit")
        status=child.expect(["[Oo]peration","[fF]ailed","#",TIMEOUT,EOF])
        if status!=2:
                print "Commit failed"
        child.sendline("review")
        child.expect("#")
	sleep(1)
	child.sendline("exit")
	child.expect(">")
	child.sendline("show system date")
	child.expect(">")
	child.sendline("config app "+app)
	child.expect("#")
	stdout.flush()

def configure_others(child):
	x=True
	for port in range(1,65536):
		x = not x   #Toggle ipv4 and ipv6 addresses
		if x:
			child.sendline("streaming ip "+str(inet_ntoa(pack('>I',randint(0,0xffffffff)))))
		else:
			child.sendline("streaming ip "+str(IPAddress(getrandbits(128))))

		child.expect("#")
		rev_comm(child)
	
		child.sendline("listenerport "+str(randint(0,65536)))
		child.expect("#")
		rev_comm(child)

		child.sendline("streaming port "+str(port))
		child.expect("#")
		rev_comm(child)
	
		for rate in range(0,5001,100):
			child.sendline("security certificate-attachrate "+str(rate))
			child.expect("#")
			rev_comm(child)
		stdout.flush()
	

#*******************************START**************************************#

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
		stdout.flush()
		exit_flag = 1
                exit(1)

	child.logfile_read=open("DsrcProxyStatus.txt",'w')
        child.timeout=Timeout

        while True:
                status=child.expect(["[pP]assword","[yY]es/[nN]o","[yY]/[nN]","[cC]onnection",\
                                                        "[Nn]o [rR]oute",TIMEOUT,EOF])
                if status==0:
                        child.sendline(passwd)
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
			stdout.flush()
                        exit(1)

        status=child.expect(["root@*","[pP]ermission","[wW]rong","[iI]nvalid",TIMEOUT,EOF])
        if status!=0:
                print "[",status,"]","Invalid Password or Timed Out"
		stdout.flush()
		exit_flag = 1
                exit(1)

        child.sendline("sav_cmd")
        status=child.expect([">",TIMEOUT,EOF])
        if status!=0:
                print "[",status,"]","Didn't enter CLI"
		stdout.flush()
		exit_flag = 1
                exit(1)

        child.sendline("config app "+app)
        status=child.expect(["[cC]ommand","[iI]nvalid","#",TIMEOUT,EOF])
        if status!=2:
                print "Invalid command"
		stdout.flush()
		exit_flag = 1
                exit(1)

	child.sendline("disable")
        child.expect("#")
        rev_comm(child)

	child.sendline("tcdlisten disable")
	child.expect("#")
	rev_comm(child)

	child.sendline("listenerport 1024")
	child.expect("#")
	rev_comm(child)

	child.sendline("streaming port 1025")
	child.expect("#")
	rev_comm(child)

	child.sendline("enable")
        child.expect("#")
        rev_comm(child)

	child.sendline("streaming mode enable send")
	child.expect("#")
	rev_comm(child)
	configure_others(child)

	child.sendline("streaming mode enable receive")
	child.expect("#")
	rev_comm(child)
	configure_others(child)

	child.sendline("streaming mode disable")
	child.expect("#")
	rev_comm(child)
	configure_others(child)
	stdout.flush()

except KeyboardInterrupt:
	stdout.flush()
	system("cat DsrcProxyStatus.txt | grep -A6 -B4 -Ei 'failed|invalid|\^command|parameter|timedout' > DsrcProxyError.txt")
	system("if [ `cat DsrcProxyError.txt | wc -l` -eq 0 ] ; then rm DsrcProxyError.txt ;fi")
	exit(0)
except SystemExit:
    if not exit_flag:
	system("cat DsrcProxyStatus.txt | grep -A6 -B4 -Ei 'failed|invalid|\^command|parameter|timedout' > DsrcProxyError.txt")
	system("if [ `cat DsrcProxyError.txt | wc -l` -eq 0 ] ; then rm DsrcProxyError.txt ;fi")
	stdout.flush()
	exit(0)
    else:
	exit(1)
except:
	print "Exception",exc_info()
	system("cat DsrcProxyStatus.txt | grep -A6 -B4 -Ei 'failed|invalid|\^command|parameter|timedout' > DsrcProxyError.txt")
	system("if [ `cat DsrcProxyError.txt | wc -l` -eq 0 ] ; then rm DsrcProxyError.txt ;fi")
	stdout.flush()
	exit(1)
