#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from os import system

app		= "dsrcforwd"
Timeout		= 300
passwd		= ""
exit_flag	= 0

#Configuration Start
psidlist	= [0xBFF0,0XBFE0,0x00,0x20,0x8003]
rsuid		= "4294967295"
rssi		= "-75"
dest_ip		= "192.168.20.72"
protocol	= "UDP"
dest_port	= "5567"
infusion_header	= "enable"
infusion_type	= "1"
msg_interval	= "1"
start_time	= ""
stop_time	= ""
#Configuration End

def rev_comm(child):
        child.sendline("review")
        child.expect("#")
        child.sendline("commit")
        status=child.expect(["[Oo]peration","[fF]ailed","#",TIMEOUT,EOF])
        if status!=2:
                print "Commit failed"
		stdout.flush()
                exit(1)
        child.sendline("review")
        child.expect("#")
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

def configure_psids(child):

	delete_all_psids(child)


	for i in psidlist:
		child.sendline("psid "+str(hex(i)))
		status=child.expect( ["Max[ ]*limit[ ]*reached","[eE]xists",TIMEOUT],3 ) #Redundancy:DualExpect
		if status==0:
			break;
		elif status==1:
			pass;
		child.expect(str(hex(i))+"#")

		child.sendline("rssi "+str(rssi))
		child.expect(str(hex(i)))

		child.sendline("message-interval "+str(msg_interval))
		child.expect(str(hex(i)))

		child.sendline("infusion-header "+infusion_header)
		child.expect(str(hex(i)))

		child.sendline("infusion-msgtype "+str(infusion_type))
		child.expect(str(hex(i)))

		child.sendline("destination protocol "+protocol)
		child.expect(str(hex(i)))
	
		child.sendline("destination ip "+dest_ip)
		child.expect(str(hex(i)))

		child.sendline("destination port "+str(dest_port))
		child.expect(str(hex(i)))

		if start_time != "" and stop_time != "":
			child.sendline("delivery-time "+start_time+" "+stop_time)
		else:
			child.sendline("delivery-time NULL NULL")
		child.expect(str(hex(i)))

		child.sendline("exit")
		child.expect("#")

		rev_comm(child)
		stdout.flush()

	
def configure_others(child):
	
	child.sendline("rsu-id "+rsuid)
	child.expect("#")

	rev_comm(child)

	stdout.flush()

	configure_psids(child)
	return
	

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
		exit_flag=1
                exit(1)

	child.logfile_read=open("DsrcForwardStatus.txt",'wb')
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
			exit_flag=1
                        exit(1)

        status=child.expect(["root@*","[pP]ermission","[wW]rong","[iI]nvalid",TIMEOUT,EOF])
        if status!=0:
                print "[",status,"]","Invalid Password or Timed Out"
		stdout.flush()
		exit_flag=1
                exit(1)

        child.sendline("sav_cmd")
        status=child.expect([">",TIMEOUT,EOF])
        if status!=0:
                print "[",status,"]","Didn't enter CLI"
		stdout.flush()
		exit_flag=1
                exit(1)

        child.sendline("config app "+app)
        status=child.expect(["[cC]ommand","[iI]nvalid","#",TIMEOUT,EOF])
        if status!=2:
                print "Invalid command"
		stdout.flush()
		exit_flag=1
                exit(1)

	child.sendline("enable")
	child.expect("#")

	configure_others(child)
	stdout.flush()
	print "",
	exit(0)

except KeyboardInterrupt:
	stdout.flush()
	exit(0)
except (SystemExit,TIMEOUT,EOF):
   if not exit_flag:
	system("cat DsrcForwardStatus.txt | grep -A1 -B2 -Ei 'failed|invalid|\^command|parameter|timedout' > DsrcForwardError.txt")
	system("if [ `cat DsrcForwardError.txt | wc -l` -eq 0 ]; then rm DsrcForwardError.txt ; fi")
	stdout.flush()
	exit(1)
   else:
	exit(0)
except:
	print "Exception",exc_info()
	system("cat DsrcForwardStatus.txt| grep -A1 -B2 -Ei 'failed|invalid|\^command|parameter|timedout' > DsrcForwardError.txt")
	system("if [ `cat DsrcForwardError.txt | wc -l` -eq 0 ]; then rm DsrcForwardError.txt ; fi")
	stdout.flush()
	exit(1)
