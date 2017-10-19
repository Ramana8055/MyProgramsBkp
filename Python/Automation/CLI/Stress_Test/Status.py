#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system
from time import sleep

Timeout		= 300
Passwd		= ""
sshcmd		= "ssh -p51012 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"

shwcmd 		= "show app_status "
uptimecmd 	= "rse_uptime "
statscmd 	= "show app "

def Usage():
	print "Usage:"
	print "\t",argv[0],"<board-ip>"
	exit(1)

def check_output(child):
	status = child.expect(["[fF]ailed","[cC]ommand [nN]ot","[iI]nvalid","Savari>>",TIMEOUT,EOF])

	if status > 3:
		print("SSH Connection Timedout or EOF reached")
		exit(1)

	sleep(1)
	child.sendline("show system date")
	child.expect("Savari>>")
	
def show_stats(child):
	"""
	child.sendline(statscmd+" status")
	check_output(child)

	child.sendline(shwcmd+" timapp")
	check_output(child)

	child.sendline(uptimecmd+" -T")
	check_output(child)

	child.sendline(statscmd+" store-and-repeat")

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(shwcmd+" ipv6-provider")
	check_output(child)

	child.sendline(uptimecmd+" -i")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(shwcmd+" dsrcforwd")
	check_output(child)

	child.sendline(uptimecmd+" -D")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(shwcmd+" dsrcproxy")
	check_output(child)

	child.sendline(uptimecmd+" -d")
	check_output(child)

	child.sendline(statscmd+" immediate-forward")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(shwcmd+" wsmpforwd")
	check_output(child)

	child.sendline(uptimecmd+" -w")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(shwcmd+" bsmforwd")
	check_output(child)

	child.sendline(uptimecmd+" -b")
	check_output(child)

	child.sendline("show system uptime")
	check_output(child)

	child.sendline(uptimecmd+" -g")
	check_output(child)

	child.sendline(uptimecmd+" -$")
	check_output(child)

	child.sendline(uptimecmd+" -@")
	check_output(child)

	child.sendline(uptimecmd+" -c")
	check_output(child)

	child.sendline(uptimecmd+" -s")
	check_output(child)

	child.sendline(uptimecmd+" -S")
	check_output(child)

	child.sendline(uptimecmd+" -H")
	check_output(child)

	#child.sendline(uptimecmd+" -M")
	#check_output(child)  #obsolete

	child.sendline(uptimecmd+" -t")
	check_output(child)

	child.sendline(uptimecmd+" -G")
	check_output(child)

	child.sendline("Reboot stats")
	check_output(child)
	"""

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

	while True:
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
