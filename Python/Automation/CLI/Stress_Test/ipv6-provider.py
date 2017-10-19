#!/usr/bin/python -B
from sys import stdout,exit,exc_info,argv
from time import time,sleep
from pexpect import spawn,TIMEOUT,EOF
from os import system
from netaddr.ip import IPAddress
from random import getrandbits,randint
from socket import inet_ntoa
from struct import pack

app		= "ipv6-provider"
Timeout		= 100
passwd		= ""
wsa_toggle	= True
wra_toggle	= True
exit_flag	= 0

def random_MAC():
	mac=[ randint(0x00,0xff),
	      randint(0x00,0xff),
	      randint(0x00,0xff),
	      randint(0x00,0xff),
	      randint(0x00,0xff),
	      randint(0x00,0xff)]

	return ':'.join(map(lambda x: "%02x" %x,mac))

def rev_comm(child):
	child.sendline("review")
	child.expect("#")
	child.sendline("commit")
	status=child.expect(["[fF]ailed","[iI]nvalid","[cC]ommand","#",TIMEOUT,EOF])
	if status != 3:
		print "Commit Failed"
	sleep(1)
	child.sendline("exit")
	child.expect(">")
	child.sendline("show system date")
	child.expect(">")
	child.sendline("config app "+app)
	child.expect("#")
	stdout.flush()

def config_wsa(child):
	global wsa_toggle
	wsa_toggle=not wsa_toggle
	child.sendline("wsa psid "+str(hex(randint(0,0xFFFFFFFF))))
	child.expect("#")
	if wsa_toggle:
		child.sendline("wsa security enable")
	else:
		child.sendline("wsa security disable")
	child.expect("#")
	child.sendline("wsa priority "+str(randint(0,100)))
	child.expect("#")
	#Add advertiser-id and service context here
	if wsa_toggle: 
		child.sendline("wsa ipv6addr "+str(IPAddress(getrandbits(128))))
	else: #ipv4 compatible ipv6 address
		child.sendline("wsa ipv6addr ::"+str(inet_ntoa(pack('>I',randint(0,0xffffffff)))))
	child.expect("#")
	child.sendline("wsa port "+str(randint(0,65536)))
	child.expect("#")
	child.sendline("wsa mac "+str(random_MAC()))
	child.expect("#") 
	child.sendline("wsa repeat-rate "+str(randint(0,256)))
	child.expect("#")
	rev_comm(child)

def config_wra(child):
	global wra_toggle
	wra_toggle=not wra_toggle
	child.sendline("wra lifetime "+str(randint(0,65536)))
	child.expect("#")
	if wra_toggle:
		child.sendline("wra prefix "+str(IPAddress(getrandbits(128))))
	else:
		child.sendline("wra prefix ::"+str(inet_ntoa(pack('>I',randint(0,0xffffffff)))))
	child.expect("#")
	child.sendline("wra prefixlen "+str(randint(0,128)))
	child.expect("#")
	if wra_toggle:   #ipv4 compatible ipv6 address
		child.sendline("wra gateway-address ipv6 ::"+str(inet_ntoa(pack('>I',randint(0,0xffffffff)))))
	else:
		child.sendline("wra gateway-address ipv6 "+str(IPAddress(getrandbits(128))))
	child.expect("#")
	child.sendline("wra gateway-address mac "+str(random_MAC()))
	child.expect("#")
	if wra_toggle:
		child.sendline("wra dns primary "+str(IPAddress(getrandbits(128))))
	else:
		child.sendline("wra dns primary ::"+str(inet_ntoa(pack('>I',randint(0,0xffffffff)))))
	child.expect("#")
	rev_comm(child)

#**********************************************START***************************************#	
try:
	if len(argv)!=2:
		exit_flag = 1
		print "Usage"
		print "\t",argv[0],"<board ip>"
		exit(1)

	ip=argv[1]
	system("rm -rf ~/.ssh/known_hosts")

	try:	
		child=spawn("ssh -p 51012 root@"+ip)
	except:
		print "ssh failed",exc_info()
		exit_flag = 1
		exit(1)

	child.logfile_read=open("Ipv6appStatus.txt",'w')
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


        child.sendline("config app "+app)
        status=child.expect(["[cC]ommand","[iI]nvalid","#",TIMEOUT,EOF])
        if status!=2:
                print "Invalid command"
		exit_flag = 1
                exit(1)
        child.sendline("enable")
        child.expect("#")


	while True:
		child.sendline("enable")
		child.expect("#")
		config_wsa(child)
		config_wra(child)	

except KeyboardInterrupt:
	system("cat Ipv6appStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > Ipv6appError.txt")
	system("if [ `cat Ipv6appError.txt |wc -l` -eq 0 ] ; then rm Ipv6appError.txt ; fi")
	exit(0)
except SystemExit:
	if not exit_flag:
		system("cat Ipv6appStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > Ipv6appError.txt")
		system("if [ `cat Ipv6appError.txt |wc -l` -eq 0 ] ; then rm Ipv6appError.txt ; fi")
		exit(0)
	else:
		exit(1)
except:
	system("cat Ipv6appStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > Ipv6appError.txt")
	system("if [ `cat Ipv6appError.txt |wc -l` -eq 0 ] ; then rm Ipv6appError.txt ; fi")
	print "Exception",exc_info()
	exit(1)
