#!/usr/bin/python -B
from sys import stdout,exit,exc_info,argv
from pexpect import spawn,TIMEOUT,EOF
from os import system

app		= "ipv6-provider"
Timeout		= 100
passwd		= ""
exit_flag	= 0

#Configuration Start
wsa_mac		= "00:1c:55:01:02:03"
wsa_ipv6addr	= "FFF0::2"
wsa_psid	= "0x23"
wsa_priority	= "31"
wsa_advtID	= "USDOT"
wsa_sercontext	= "SCMS"
wsa_port	= "16092"
wsa_repeatrate	= "50"

wra_prefix	= "FFE0::3"
wra_prefix_len	= "64"
wra_gw_mac	= "00:1c:54:01:02:03"
wra_gw_ipv6addr	= "FFD0::4"
wra_primary_dns	= "FFD0::1"
wra_lifetime	= "1800"
#Configuration End

def rev_comm(child):
	child.sendline("review")
	child.expect("#")
	child.sendline("commit")
	status=child.expect(["[fF]ailed","[iI]nvalid","[cC]ommand","#",TIMEOUT,EOF])
	if status != 3:
		print "Commit Failed"
		exit(1)
	child.sendline("exit")
	child.expect(">")
	child.sendline("show system date")
	child.expect(">")
	child.sendline("config app "+app)
	child.expect("#")
	stdout.flush()

def config_wsa(child):

	child.sendline("wsa psid "+wsa_psid)
	child.expect("#")

	if security == "securityEnable":
		child.sendline("wsa security enable")
	else:
		child.sendline("wsa security disable")
	child.expect("#")

	child.sendline("wsa priority "+str(wsa_priority))
	child.expect("#")

	child.sendline("wsa advertiser-id "+wsa_advtID)
	child.expect("#")

	child.sendline("wsa service-context "+wsa_sercontext)
	child.expect("#")

	child.sendline("wsa ipv6addr "+wsa_ipv6addr)
	child.expect("#")

	child.sendline("wsa port "+str(wsa_port))
	child.expect("#")

	child.sendline("wsa mac "+wsa_mac)
	child.expect("#") 

	child.sendline("wsa repeat-rate "+str(wsa_repeatrate))
	child.expect("#")

def config_wra(child):
	child.sendline("wra lifetime "+str(wra_lifetime))
	child.expect("#")

	child.sendline("wra prefix "+wra_prefix)
	child.expect("#")

	child.sendline("wra prefixlen "+str(wra_prefix_len))
	child.expect("#")

	child.sendline("wra gateway-address ipv6 "+wra_gw_ipv6addr)
	child.expect("#")

	child.sendline("wra gateway-address mac "+wra_gw_mac)
	child.expect("#")

	child.sendline("wra dns primary "+wra_primary_dns)
	child.expect("#")

#**********************************************START***************************************#	
try:
	if len(argv)!=3:
		exit_flag = 1
		print "Usage"
		print "\t",argv[0],"<board ip> <securityEnable/securityDisable>"
		exit(1)

	ip=argv[1]
	security=argv[2]

	if security != "securityEnable" and security != "securityDisable":
		print "Usage"
		print "\t",argv[0],"<board ip> <securityEnable/securityDisable>"
		exit_flag = 1
		exit(1)
		
	system("rm -rf ~/.ssh/known_hosts")

	try:	
		child=spawn("ssh -p 51012 root@"+ip)
	except:
		print "ssh failed",exc_info()
		exit_flag = 1
		exit(1)

	child.logfile_read=open("Ipv6appStatus.txt",'wb')
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
			exit_flag = 1
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
	config_wsa(child)
	config_wra(child)
	rev_comm(child)	
	exit(0)

except KeyboardInterrupt:
	exit(0)
except (SystemExit,TIMEOUT,EOF):
   if not exit_flag:
	system("cat Ipv6appStatus.txt | grep -A1 -B2 -Ei '\^command|failed|invalid|parameter|timedout' > Ipv6appError.txt")
	system("if [ `cat Ipv6appError.txt | wc -l` -eq 0 ] ; then rm Ipv6appError.txt ; fi")
	exit(1)
   else:
	exit(0)
except:
	system("cat Ipv6appStatus.txt | grep -A1 -B2 -Ei '\^command|failed|invalid|parameter|timedout' > Ipv6appError.txt")
	system("if [ `cat Ipv6appError.txt | wc -l` -eq 0 ] ; then rm Ipv6appError.txt ; fi")
	print "Exception",exc_info()
	exit(1)
