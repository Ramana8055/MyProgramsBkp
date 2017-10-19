#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system
from time import sleep

passwd	= ""

apps=["ipv6-provider","immediate-forward","dsrc-message-forward","bsmforwd","wsmpforwd","store-repeat","tcd","gpsoutput","radio"]

operation_timeout_count		= 0
read_operation_failed_count	= 0
write_operation_failed_count	= 0
app_failed_count		= 0
connect_failed_count		= 0
packet_size_error_count		= 0
broken_pipe_count		= 0

commit_count	= 0
exit_flag	= 0
Timeout		= 300

def Usage():
	global exit_flag
	exit_flag=1
	print "Usage:"
	print "\t",argv[0],"<board-ip> <App>"
	print "\t App can be one of ipv6-provider,immediate-forward,dsrc-message-forward,bsmforwd,wsmpforwd,store-repeat,tcd,gpsoutput,radio\n"
	exit(1)

def execute(child,cmd):
	global operation_timeout_count,read_operation_failed_count
	global write_operation_failed_count
	global app_failed_count,connect_failed_count
	global packet_size_error_count,commit_count
	global broken_pipe_count
	
	while True:
		child.sendline(cmd)
		child.expect("#")
		child.sendline("review")
		#child.expect("#")
		#child.sendline("commit")
		status=child.expect(["[aA]ppliaction","[cC]onnection [aA]ttempt","[rR]ead","[wW]rite",\
						"[oO]peration","[rR]eceived","[bB]roken","#",EOF,TIMEOUT])
		if status==0:
			app_failed_count +=1
		elif status==1:
			connect_failed_count +=1
		elif status==2:
			read_operation_failed_count +=1
		elif status==3:
			write_operation_failed_count +=1
		elif status==4:
			operation_timeout_count +=1
		elif status==5:
			packet_size_error_count +=1
			exit(1)
		elif status==6:
			broken_pipe_count += 1
			exit(1)
		elif status==8 or status==9:
			print "Connection Timeout or EOF reached"
			exit(1)
		sleep(1)
		child.sendline("exit")
		child.expect(">")
		child.sendline("show system date")
		child.expect(">")
		child.sendline("config app "+app)
		child.expect("#")
		
		#commit_count +=1

try:

	if len(argv)!=3:
		Usage()

	ip=argv[1]
	app=argv[2]

	if not app in apps:
		print "Invalid app",app
		Usage()

	status_file=app+"_status.txt"
	try:
		log_file=open(status_file,'wb')
	except:
		print "Open Failed",exc_info()[0]
		exit(1)

	system("rm -rf ~/.ssh/known_hosts")
	try:
		child=spawn("ssh -p51012 root@"+ip)
	except:
		print "ssh failed",exc_info()
		exit(1)
	child.logfile_read=log_file
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
                exit(1)

        child.sendline("sav_cmd")
        status=child.expect([">",TIMEOUT,EOF])
        if status!=0:
                print "[",status,"]","Couldn't enter CLI"
                exit(1)
	
	child.sendline("config app "+app)
	child.expect("#")


	if app=="gpsoutput":
		execute(child,"port 5115")
	elif app=="radio":
		execute(child,"dsrc0_chmode 1")
	else:
		execute(child,"enable")				
		

except KeyboardInterrupt:
	print "\033[32m\nStats:"
	print "\tTotal Number of Commits:\t",commit_count
	print "\tApp Failed to Restart Count:\t",app_failed_count
	print "\tRead Operation Failed Count:\t",read_operation_failed_count
	print "\tWrite Operation Failed Count:\t",write_operation_failed_count
	print "\tOperation Timed Out Count:\t",operation_timeout_count
	print "\tReceived Invalid Packet Size Count:\t",packet_size_error_count
	print "\tConnection Attemt Failed Count:\t", connect_failed_count
	print "\tBroken Pipe Count:\t", broken_pipe_count
	print "\033[0m"
	system("cat "+app+"_status.txt | grep -A2 -B4 -Ei 'failed|invalid|\^command|parameter|timedout' > "+app+"_Error.txt")
	system("if [ `cat "+app+"_Error.txt | wc -l ` -eq 0 ]; then rm "+app+"_Error.txt ; fi")
	exit(0)
except SystemExit:
	if exit_flag==0:
		print "\033[32m\nStats:"
		print "\tTotal Number of Commits:\t",commit_count
		print "\tApp Failed to Restart Count:\t",app_failed_count
		print "\tRead Operation Failed Count:\t",read_operation_failed_count
		print "\tWrite Operation Failed Count:\t",write_operation_failed_count
		print "\tOperation Timed Out Count:\t",operation_timeout_count
		print "\tReceived Invalid Packet Size Count:",packet_size_error_count
		print "\tConnection Attemt Failed Count:\t", connect_failed_count
		print "\tBroken Pipe Count:\t", broken_pipe_count
		print "\033[0m"
		system("cat "+app+"_status.txt | grep -A1 -B4 -Ei 'failed|invalid|\^command|parameter|timedout' > "+app+"_Error.txt")
		system("if [ `cat "+app+"_Error.txt | wc -l ` -eq 0 ]; then rm "+app+"_Error.txt ; fi")
		exit(0)
	else:
		exit(1)
except (TIMEOUT,EOF):
	print("Network is down")
	system("cat "+app+"_status.txt | grep -A2 -B4 -Ei 'failed|invalid|\^command|parameter|timedout' > "+app+"_Error.txt")
	system("if [ `cat "+app+"_Error.txt | wc -l ` -eq 0 ]; then rm "+app+"_Error.txt ; fi")
	exit(1)
except:
	print "Global Exception",exc_info()
	system("cat "+app+"_status.txt | grep -A2 -B4 -Ei 'failed|invalid|\^command|parameter|timedout' > "+app+"_Error.txt")
	system("if [ `cat "+app+"_Error.txt | wc -l ` -eq 0 ]; then rm "+app+"_Error.txt ; fi")
	exit(1)
