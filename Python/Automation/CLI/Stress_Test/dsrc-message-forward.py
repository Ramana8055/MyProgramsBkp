#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system
from struct import pack
from random import randint,getrandbits
from time import time,sleep
from socket import inet_ntoa
from netaddr.ip import IPAddress,IPNetwork

app		= "dsrc-message-forward"
Timeout		= 300
passwd		= ""
exit_flag	= 0
toggle		= True

def rev_comm(child):
        child.sendline("review")
        child.expect("#")
        child.sendline("commit")
        status=child.expect(["[Oo]peration","[fF]ailed","#",TIMEOUT,EOF])
        if status!=2:
                print "Commit failed"
		stdout.flush()
        child.sendline("review")
        child.expect("#")
	sleep(1)
	child.sendline("exit")
	child.expect(">")
	child.sendline("show system date")
	child.expect(">")
	child.sendline("config app "+app)
	child.expect("#")

def delete_all_psids(child):
	while True:
		child.sendline("review")
		child.expect("[pP]sid[ ]*=[ ]*0x[a-fA-F0-9]*")
		child.sendline("delete "+child.match.group().split("=")[1])
		sleep(1)
		status=child.expect(["Cannot delete",TIMEOUT],3) #Redundancy:Dual Expect
		if status==0:
			break
		elif status==1:
			pass
		child.expect("#")
		stdout.flush()
		rev_comm(child)

def configure_ten_psids(child):

	global toggle

	toggle = not toggle

	delete_all_psids(child)

	psidlist=[
			randint(0x0,0x7f),
			randint(0x0,0x7f),
			randint(0x8000,0xbfff),
			randint(0x8000,0xbfff),
			randint(0xc00000,0xdfffff),
			randint(0xc00000,0xdfffff),
			randint(0xc00000,0xdfffff),
			randint(0xe0000000,0xefffffff),
			randint(0xe0000000,0xefffffff),
			randint(0xe0000000,0xefffffff)
		]

	newlist=[] #Store the values

	for i in psidlist:
		newlist.append(i)

	for i in newlist:
		k=str(hex(i))
		child.sendline("psid "+k)
		status=child.expect( ["Max[ ]*limit[ ]*reached",TIMEOUT],3 ) #Redundancy:DualExpect
		if status==0:
			break;
		elif status==1:
			pass;
		child.expect(k+"#")
		child.sendline("rssi "+str(randint(-101,-59)))
		child.expect(k)
		child.sendline("message-interval "+str(randint(1,11)))
		child.expect(k)
		if toggle:
			child.sendline("infusion-header enable")
		else:
			child.sendline("infusion-header disable")
		child.expect(k)

		if toggle:
			child.sendline("destination protocol TCP")
		else:
			child.sendline("destination protocol UDP")
		child.expect(k)
	
		j=randint(0,1)

		if j:
			child.sendline("destination ip "+str(inet_ntoa(pack('>I',randint(0,0xffffffff)))))
		else:
			child.sendline("destination ip "+str(IPAddress(getrandbits(128))))
		child.expect(k)

		child.sendline("destination port "+str(randint(0,65536)))
		child.expect(k)

		#delivery time has to be added

		child.sendline("exit")
		child.expect("#")

		rev_comm(child)
		stdout.flush()

	
def configure_others(child):
	
	child.sendline("rsu-id "+str( randint(0, 4294967296) ))
	child.expect("#")

	rev_comm(child)

	stdout.flush()

	configure_ten_psids(child)
	

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

	child.logfile_read=open("DsrcForwardStatus.txt",'w')
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

	child.sendline("enable")
	child.expect("#")

	while True:
		configure_others(child)
		stdout.flush()

except KeyboardInterrupt:
	system("cat DsrcForwardStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > DsrcForwardError.txt")
	system("if [ `cat DsrcForwardError.txt |  wc -l ` -eq 0 ] ; then rm DsrcForwardError.txt ;fi")
	stdout.flush()
	exit(0)
except SystemExit:
    if not exit_flag:
	system("cat DsrcForwardStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > DsrcForwardError.txt")
	system("if [ `cat DsrcForwardError.txt |  wc -l ` -eq 0 ] ; then rm DsrcForwardError.txt ;fi")
	stdout.flush()
	exit(0)
    else:
	exit(1)
except:
	print "Exception",exc_info()
	system("cat DsrcForwardStatus.txt | grep -A1 -B3 -Ei 'failed|invalid|\^command|parameter|timedout' > DsrcForwardError.txt")
	system("if [ `cat DsrcForwardError.txt |  wc -l ` -eq 0 ] ; then rm DsrcForwardError.txt ;fi")
	stdout.flush()
	exit(1)
