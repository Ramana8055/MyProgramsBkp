#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system

app		= "radio"
Timeout		= 100
passwd		= ""
exit_flag	= 0

#Configuration Start

dsr0_chmode	= "1"
dsrc0_svc	= "174"
dsrc1_chmode	= "0"
dsrc1_svc	= "184"

#Configuration End

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
	child.expect("Savari>>")
	child.sendline("show system date")
	child.expect("Savari>>")
	child.sendline("config app "+app)
	child.expect("#")
	stdout.flush()
def Usage():
	global exit_flag
	exit_flag = 1
	print "Usage:"
	print "\t",argv[0],"<board ip>"
	exit(1)

#*******************************START**************************************#

try:
	if len(argv)!=2:
		Usage()

	ip=argv[1]
        system("rm -rf ~/.ssh/known_hosts")

        try:
                child=spawn("ssh -p51012 root@"+ip)
        except:
                print "ssh failed",exc_info()
		stdout.flush()
		exit_flag = 1
                exit(1)

	child.logfile_read=open("RadioStatus.txt",'wb')
	#child.logfile_read=stdout
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
			stdout.flush()
			exit_flag = 1
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


	child.sendline("dsrc0 chan_mode "+str(dsr0_chmode))
	child.expect("#")

	child.sendline("dsrc0 svc "+str(dsrc0_svc))
	child.expect("#")

	child.sendline("dsrc1 chan_mode "+str(dsrc1_chmode))
	child.expect("#")

	child.sendline("dsrc1 svc "+str(dsrc1_svc))
	child.expect("#")

	rev_comm(child)
	exit(0)

except KeyboardInterrupt:
	stdout.flush()
	exit(0)
except (SystemExit,TIMEOUT,EOF):
    if not exit_flag:
	stdout.flush()
	system("cat RadioStatus.txt | grep -A1 -B2 -Ei 'failed|invalid|\^command|parameter|timedout' > RadioError.txt")
	system("if [ `cat RadioError.txt|wc -l` -eq 0 ] ; then rm RadioError.txt ; fi")
	exit(0)
    else:
	exit(1)
except:
	print "Exception",exc_info()
	system("cat RadioStatus.txt | grep -A1 -B2 -Ei 'failed|invalid|\^command|parameter|timedout' > RadioError.txt")
	system("if [ `cat RadioError.txt|wc -l` -eq 0 ] ; then rm RadioError.txt ; fi")
	stdout.flush()
	exit(1)
