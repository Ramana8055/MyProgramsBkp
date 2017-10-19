#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system
from time import sleep

Timeout		= 300
Passwd		= ""
sshcmd		= "ssh -p51012 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"

shwcmd 		= "show app_status "
uptimecmd 	= "show rsu uptime "
statscmd 	= "show rsu stats "

def Usage():
	print "Usage:"
	print "\t",argv[0],"<board-ip>"
	exit(1)

def check_output(child):
	status = child.expect(["[fF]ailed","[cC]ommand [nN]ot","[iI]nvalid","Savari>>",TIMEOUT,EOF])

	if status > 3:
		print("SSH Connection Timedout or EOF reached")
		exit(1)

	child.sendline("show system date")
	child.expect("Savari>>")
	sleep(1)
	
def show_stats(child):

	child.sendline("show app status")
	check_output(child)

	child.sendline("show app immediate-forward")
	check_output(child)

	child.sendline("show app store-and-repeat")
	check_output(child)

	child.sendline(shwcmd+" dsrcproxy")
	check_output(child)

	child.sendline(shwcmd+" ipv6app")
	check_output(child)

	child.sendline(shwcmd+" dsrc-message-forward")
	check_output(child)

	child.sendline(statscmd+" bsm_forward")
	check_output(child)

	child.sendline(uptimecmd+" bsm-forwd")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(statscmd+" tim")
	check_output(child)

	child.sendline(uptimecmd+" timApp")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(statscmd+" dsrcproxy")
	check_output(child)

	child.sendline(uptimecmd+" dsrcproxy")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(statscmd+" wsa")
	check_output(child)

	child.sendline(uptimecmd+" ipv6app")
	check_output(child)

	child.sendline(statscmd+" wsmp_forward")
	check_output(child)

	child.sendline(uptimecmd+" wsmp-forwdx")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(statscmd+" dsrcforwad")
	check_output(child)

	child.sendline(uptimecmd+" dsrc-forwd")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(uptimecmd+" gpsd")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(uptimecmd+" smgrd")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(uptimecmd+" sdiskmgr")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(uptimecmd+" cycurV2X-bin")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(uptimecmd+" savari16093d-ath0")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(uptimecmd+" savari16093d-ath1")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(uptimecmd+" heartbeat")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(uptimecmd+" tCd")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(uptimecmd+" sinit")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline("Reboot stats")
	check_output(child)

	child.sendline("show system gpsstatus")
	check_output(child)

	child.sendline("show version")
	check_output(child)

	child.sendline("show system process-list")
	check_output(child)

	child.sendline("ping ipv4 192.168.20.9")
	check_output(child)

	child.sendline("show traceroute 192.168.20.9")
	check_output(child)

	child.sendline("show system disk-usage")
	check_output(child)

	child.sendline("show system memory-usage")
	check_output(child)

	child.sendline("show system cpu-usage 5")
	check_output(child)

	exit(0)

try:

	if len(argv)!=2:
		Usage()

	ip=argv[1]
	try:
		child=spawn( sshcmd+ip)
	except:
		print "ssh failed",exc_info()
		exit(1)
	child.logfile_read=open("RseStats.txt",'wb')
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
                        exit(1)

        status=child.expect(["root@*","[pP]ermission","[wW]rong","[iI]nvalid",TIMEOUT,EOF])
        if status!=0:
                print "[",status,"]","Invalid Password or Timed Out"
                exit(1)

        child.sendline("sav_cmd")
        status=child.expect([">",TIMEOUT,EOF])
        if status!=0:
                print "[",status,"]","Couldn't enter CLI"
                exit(1)

	show_stats(child)
	exit(0)
			
except KeyboardInterrupt:
	exit(0)
except SystemExit:
	exit(1)
except (TIMEOUT,EOF):
	print("Network is down")
	exit(1)
except:
	print "Global Exception",exc_info()
	exit(1)
