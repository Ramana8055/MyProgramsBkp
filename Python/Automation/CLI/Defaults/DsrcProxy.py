#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system

app		= "dsrcproxy"
Timeout		= 100
passwd		= ""
exit_flag	= 0

#Configuration Start
streaming_ip	= "192.168.20.72"
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
	child.sendline("exit")
	child.expect(">")
	child.sendline("show system date")
	child.expect(">")
	child.sendline("config app "+app)
	child.expect("#")
	stdout.flush()
def Usage():
	global exit_flag
	exit_flag = 1
	print "Usage:"
	print "\t",argv[0],"<board ip> <streamingmode> <TcdlistenStatus>"
	print "\t","Streaming mode can be one of (send,disable,receive)"
	print "\t","Tcdlistenstatus can be Tcdenable/Tcddisable"
	print "\t","Make sure you are running Tcd if Tcdlisten is enabled"
	exit(1)

#*******************************START**************************************#

try:
	if len(argv)!=4:
		Usage()

	ip=argv[1]
	streaming=argv[2]
	Tcdlisten=argv[3]

	if streaming != "send" and streaming != "receive" and streaming != "disable":
		Usage()
	if Tcdlisten != "Tcdenable" and Tcdlisten != "Tcddisable":
		Usage()
		
        system("rm -rf ~/.ssh/known_hosts")

        try:
                child=spawn("ssh -p51012 root@"+ip)
        except:
                print "ssh failed",exc_info()
		stdout.flush()
		exit_flag = 1
                exit(1)

	child.logfile_read=open("DsrcProxyStatus.txt",'wb')
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

	if Tcdlisten == "Tcdenable":
		child.sendline("tcdlisten enable")
	else:
		child.sendline("tcdlisten disable")
	child.expect("#")

	child.sendline("listenerport 1516")
	child.expect("#")

	child.sendline("streaming port 51015")
	child.expect("#")

	child.sendline("streaming ip "+streaming_ip)
	child.expect("#")

	child.sendline("enable")
        child.expect("#")

	if streaming == "send":
		child.sendline("streaming mode enable send")
	elif streaming == "receive":
		child.sendline("streaming mode enable receive")
	else:
		child.sendline("streaming mode disable")	
	child.expect("#")

	child.sendline("security certificate-attachrate 500")
	child.expect("#")

	child.sendline("enable")
        child.expect("#")

	rev_comm(child)
	exit(0)

except KeyboardInterrupt:
	stdout.flush()
	exit(0)
except (SystemExit,TIMEOUT,EOF):
    if not exit_flag:
	stdout.flush()
	system("cat DsrcProxyStatus.txt | grep -A1 -B2 -Ei 'failed|invalid|\^command|parameter|timedout' > DsrcProxyError.txt")
	system("if [ `cat DsrcProxyError.txt|wc -l` -eq 0 ] ; then rm DsrcProxyError.txt ; fi")
	exit(0)
    else:
	exit(1)
except:
	print "Exception",exc_info()
	system("cat DsrcProxyStatus.txt | grep -A1 -B2 -Ei 'failed|invalid|\^command|parameter|timedout' > DsrcProxyError.txt")
	system("if [ `cat DsrcProxyError.txt|wc -l` -eq 0 ] ; then rm DsrcProxyError.txt ; fi")
	stdout.flush()
	exit(1)
