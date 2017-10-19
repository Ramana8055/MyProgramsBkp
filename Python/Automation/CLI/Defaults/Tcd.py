#!/usr/bin/python
from sys import stdout,exit,exc_info,argv
from pexpect import spawn,TIMEOUT,EOF
from os import system

app		= "tcd"
app2		= "dsrcproxy"
passwd		= ""
Timeout		= 100
exit_flag	= 0

#Configuration Start

spat_tx_intvl	= "100"
spat_psid	= "0xBFE0"
spat_priority	= "7"
spat_signature	= "True"
spat_encryption	= "False"
spat_tx_enlanes	= "disable"
spat_certatrate	= "500"
spat_certopti	= "enable"


map_tx_intvl	= "1000"
map_psid	= "0xBFF0"
map_priority	= "7"
map_signature	= "True"
map_encryption	= "False"
map_per_timeout	= "2"
map_certatrate	= "1000"


send_red_states	= "enable"
detector_info	= "enable"

tc_ip		= "192.168.20.72"
tc_port		= "501"
tc_type		= "econolite"

imm_forwd_port	= "1516"

broadcast_port	= "6053"

#Configuration End

def rev_comm(child):
        child.sendline("review")
        child.expect("#")
        child.sendline("commit")
        status=child.expect(["[Oo]peration","[fF]ailed","[wW]rong [cC]onfiguration","#",TIMEOUT,EOF])
	if status == 2:
		print "\nFor 2009 standard rndf file should be used"
		print "For 2015 standard xml file should be used" 
		exit(1)
        elif status != 3:
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

def ntcip(child):
	child.sendline("mode ntcip")
	child.expect("#")

	child.sendline("ntcip tc-ipaddr "+tc_ip)
	child.expect("#")

	child.sendline("ntcip tc-port "+str(tc_port))
	child.expect("#")

	child.sendline("ntcip tc-type "+tc_type)
	child.expect("#")
	
	child.sendline("ntcip spat-tx-intvl 100")
	child.expect("#")

	child.sendline("ntcip map-tx-intvl 1000")
	child.expect("#")

	child.sendline("ntcip send-red-states "+send_red_states)
	child.expect("#")

	child.sendline("ntcip detector-info "+detector_info)
	child.expect("#")

def broadcast(child):
	child.sendline("mode broadcast")
	child.expect("#")

	child.sendline("broadcast port "+str(broadcast_port))
	child.expect("#")

def immediate_forward(child):
	child.sendline("mode immediate-forward")
	child.expect("#")

	child.sendline("immediate-forward port "+str(imm_forwd_port))
	child.expect("#")

def common(child):
	child.sendline("spat psid "+spat_psid)
	child.expect("#")

	child.sendline("spat priority "+str(spat_priority))
	child.expect("#")

	child.sendline("spat certificate-attachrate "+str(spat_certatrate))
	child.expect("#")
	
	child.sendline("spat signature "+spat_signature)
	child.expect("#")

	child.sendline("spat encryption "+spat_encryption)
	child.expect("#")
		
	child.sendline("spat transmit-enabled-lanes "+spat_tx_enlanes)
	child.expect("#")

	child.sendline("spat certificate-optimisation "+spat_certopti)
	child.expect("#")

	child.sendline("map psid "+map_psid)
	child.expect("#")

	child.sendline("map priority "+str(map_priority))
	child.expect("#")
	
	child.sendline("map persistent-timeout "+str(map_per_timeout))
	child.expect("#")

	child.sendline("map certificate-attachrate "+str(map_certatrate))
	child.expect("#")
	
	child.sendline("map signature "+map_signature)
	child.expect("#")

	child.sendline("map encryption "+map_encryption)
	child.expect("#")

def Usage():
	global exit_flag
	exit_flag = 1
	print "Usage:"
	print "\t",argv[0],"<board ip> <SAE_std(2009 or 2015)> <mode(ntcip/broadcast/immediate-forward)>"
	print "\t","Change the MapFile to xml format for 2015 std, rndf otherwise"
	exit(1)
	
def std_2009(child, mode):
	common(child)
	if mode == "ntcip":
		ntcip(child)
		rev_comm(child)
	else:
		immediate_forward(child)
		rev_comm(child)

def std_2015(child, mode):
	common(child)
	if mode == "broadcast":
		broadcast(child)
		rev_comm(child)
	elif mode == "ntcip":
		ntcip(child)
		rev_comm(child)
	else:
		immediate_forward(child)
		rev_comm(child)


#*************************************START*******************************************#
try:
	if len(argv)!=4:
		Usage()
	
	ip   =argv[1]
	std  =int(argv[2])
	mode =argv[3]

	if mode != "ntcip" and mode != "immediate-forward" and mode != "broadcast":
		print "Invalid mode",mode
		Usage()

	if mode == "broadcast" and std == 2009:
		print "2009 standard has no support for mode",mode
		Usage()

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
		print "[",status,"]","Couldn't enter CLI"
		exit_flag = 1
		exit(1)

	child.sendline("enable privileged-mode")
	child.expect("Enter password")

	child.sendline("6efre#ESpe")
	child.expect(">")

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
		std_2009(child,mode) #Make sure you change the Map File Accordingly
	elif std==2015:
		std_2015(child,mode)
	else:
		print "Invalid SAE standard",std
		Usage()
		exit(1)
	exit(0)

except KeyboardInterrupt:
	exit(0)
except SystemExit:
    if not exit_flag:
	system("cat TcdStatus.txt | grep -A1 -B4 -Ei 'failed|invalid|\^command|parameter|timedout|wrong' > TcdError.txt")
	system("if [ `cat TcdError.txt|wc -l` -eq 0 ] ; then rm TcdError.txt ; fi")
	exit(1)
    else:
	exit(0)
except:
	print "Exception",exc_info()
	system("cat TcdStatus.txt | grep -A1 -B4 -Ei 'failed|invalid|\^command|parameter|timedout|wrong' > TcdError.txt")
	system("if [ `cat TcdError.txt|wc -l` -eq 0 ] ; then rm TcdError.txt ; fi")
	exit(1)
