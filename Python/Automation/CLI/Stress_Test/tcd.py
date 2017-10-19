#!/usr/bin/python
from sys import stdout,exit,exc_info,argv
from pexpect import *
from os import system
from time import time,sleep
from socket import inet_ntoa
from struct import pack
from random import getrandbits,randint,SystemRandom

app		= "tcd"
app2		= "immediate-forward"
passwd		= ""
Timeout		= 100
toggle		= True
exit_flag	= 0

def rev_comm(child):
        child.sendline("review")
        child.expect("#")
        child.sendline("commit")
        status = child.expect(["[Oo]peration","[fF]ailed","#",TIMEOUT,EOF])
        if status != 2:
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

def ntcip(child):
	child.sendline("mode ntcip")
	child.expect("#")

	child.sendline("ntcip tc-ipaddr "+str(inet_ntoa(pack('>I',randint(0,0xffffffff)))))
	child.expect("#")

	child.sendline("ntcip tc-port "+str(randint(0,65536)))
	child.expect("#")

	#child.sendline("ntcip tc-type "+str(SystemRandom().choice(["generic","econolite","d4","siemens"])))
	#child.expect("#")
	
	child.sendline("ntcip spat-tx-intvl "+str(randint(-100,50000)))
	child.expect("#")

	child.sendline("ntcip map-tx-intvl "+str(randint(-100,50000)))
	child.expect("#")

	#SendRed-States and Detector Info

def broadcast(child):
	child.sendline("mode broadcast")
	child.expect("#")

	child.sendline("broadcast port "+str(randint(0,65536)))
	child.expect("#")

def immediate_forward(child):
	child.sendline("mode immediate-forward")
	child.expect("#")

	child.sendline("immediate-forward port "+str(randint(0,65536)))
	child.expect("#")

def common(child):
	global toggle
	toggle = not toggle
	child.sendline("spat psid "+str(hex(randint(0,0xFFFFFFFF))))
	child.expect("#")

	child.sendline("spat priority "+str(randint(-10,64)))
	child.expect("#")

	child.sendline("spat certificate-attachrate "+str(randint(-100,10000000000)))
	child.expect("#")
	
	child.sendline("spat signature "+str(toggle))
	child.expect("#")

	child.sendline("spat encryption "+str(toggle))
	child.expect("#")
		
	child.sendline("map psid "+str(hex(randint(0x0,0xffffffff))))
	child.expect("#")

	child.sendline("map priority "+str(randint(-10,64)))
	child.expect("#")
	
	child.sendline("map persistent-timeout "+str(randint(-10,2880)))
	child.expect("#")

	child.sendline("map certificate-attachrate "+str(randint(-100,1000000000)))
	child.expect("#")
	
	child.sendline("map signature "+str(toggle))
	child.expect("#")

	child.sendline("map encryption "+str(toggle))
	child.expect("#")

	if toggle:
		child.sendline("spat transmit-enabled-lanes enable")
		child.expect("#")

		child.sendline("spat certificate-optimisation enable")
		child.expect("#")
	else:
		child.sendline("spat transmit-enabled-lanes disable")
		child.expect("#")

		child.sendline("spat certificate-optimisation disable")
		child.expect("#")

def std_2009(child):
	#copy rndf
	common(child)
	ntcip(child)
	rev_comm(child)
	immediate_forward(child)
	rev_comm(child)

def std_2015(child):
	#copy xml
	common(child)
	broadcast(child)
	rev_comm(child)
	ntcip(child)
	rev_comm(child)
	immediate_forward(child)
	rev_comm(child)


#*************************************START*******************************************#
try:
	if len(argv)!=3:
		exit_flag = 1
		print "Usage:"
		print "\t",argv[0],"<board ip> <SAE_std(2009 or 2015)>"
		print "\t","\033[31mChange the MapFile to xml format for 2015 std, rndf otherwise\033[0m"
		exit(1)
	
	ip=argv[1]
	std=int(argv[2])
	system("rm -rf ~/.ssh/known_hosts")

	try:
		child=spawn("ssh -p51012 root@"+ip)
	except:
		print "ssh failed",exc_info()
		exit_flag = 1
		exit(1)

	child.logfile_read=open("TcdStatus.txt",'wb')
	child.timeout=100

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

	child.sendline("enable privileged-mode")
	child.expect("Enter password")

	child.sendline("6efre#ESpe")
	status = child.expect(["[pP]assword",">"])

	if status == 0:
		print "Wrong Privilege mode password"
		exit_flag = 1
		exit(1)

	child.sendline("config system j2735 "+str(std))
	child.expect(">")

	child.sendline("disable privileged-mode")
	child.expect(">")

	child.sendline("config app "+app)
	status=child.expect(["[cC]ommand","[iI]nvalid","#",TIMEOUT,EOF])
        if status!=2:
                print "Invalid command"
		exit_flag = 1
                exit(1)

        child.sendline("enable")
        child.expect("#")
	rev_comm(child)

	child.sendline("exit")
	child.expect(">")
	child.sendline("config app "+app2) #Enabling tcdlisten in DsrcProxy to send packets OTA
	child.expect("#")
	child.sendline("enable")
	child.expect("#")
	child.sendline("tcdlisten enable")
	child.expect("#")
	rev_comm(child)

	child.sendline("exit")
	child.expect(">")
	child.sendline("config app "+app)
	child.expect("#")

	if std==2009:
		while True:
			std_2009(child) #Make sure you change the current standard and the Map File
	elif std==2015:
		while True:
			std_2015(child)
	else:
		print "Invalid SAE standard",std
		exit_flag = 1
		exit(1)

except KeyboardInterrupt:
	system("cat TcdStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > TcdError.txt")
	system("if [ `cat TcdError.txt | wc -l` -eq 0 ] ; then rm TcdError.txt ; fi")
	exit(0)
except SystemExit:
	if not exit_flag:
		system("cat TcdStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > TcdError.txt")
		system("if [ `cat TcdError.txt | wc -l` -eq 0 ] ; then rm TcdError.txt ; fi")
		exit(0)
	else:
		exit(1)
except:
	print "Exception",exc_info()
	system("cat TcdStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > TcdError.txt")
	system("if [ `cat TcdError.txt | wc -l` -eq 0 ] ; then rm TcdError.txt ; fi")
	exit(1)
