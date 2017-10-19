#!/usr/bin/python -B
from sys import exit,exc_info,stdout,argv
from pexpect import spawn,EOF,TIMEOUT
from random import SystemRandom,randint,getrandbits
from netaddr import IPAddress
from struct import pack
from socket import inet_ntoa
from os import system
from time import sleep
from string import ascii_uppercase,ascii_lowercase,digits

#********************************************************************************

# Script to set parameters via snmp v3

# Use ./snmp.py <board ip> <csv file>
# csv file strictly should have "," as the delimiter

# Every line should contain:
# <Parameter Name>,<oid>,<Type>,<variable no of values>

# If the Type is integer the type should be "i" follwed by minVal,maxVal

# If the Type is PSID the type is "p" and next columns are ignored

# If the Type is string and takes fixed strings then use "f" follwed by fixed values
# with ":" as the delimter. For eg name,oid,f,fixedvar1:fixedvar2 and so on

# If the Type is ipaddress use "ip" as type and next columns are ignored

# If the Type is MAC address use "m" as type and next columns are ignored

# If the Type anyother string use "s" and next columns are ignored

#********************************************************************************
# Dependencies: The snmp and the python package netaddr has to be installed
# Use:
# sudo apt-get install snmp python-pip
# sudo pip install netaddr
#********************************************************************************


Timeout=100
usr="savari"  #Local user. Make sure you have root passwd if you are in root
passwd="rams@cdac20"   #Local passwd

snmpset="snmpset -v3 -u savari -a MD5 -A tUrnErf@1rb@nk$ -l authNoPriv -t 20"
snmpget="snmpget -v3 -u savari -a MD5 -A tUrnErf@1rb@nk$ -l authNoPriv -t 20" 

timeout_errors=0
exit_flag=0
invalid_value=0
commit_failed=0
out_of_range=0

def exit_negative():
	global exit_flag
	exit_flag=1
	exit(1)

def getRandomPsid():
        psid=randint(0,0xFFFFFFFF)
        return hex(psid)

def getRandomMAC():
        mac = [
                randint(0x00, 0xff),
                randint(0x00, 0xff),
                randint(0x00, 0xff),
                randint(0x00, 0xff),
                randint(0x00, 0xff),
                randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))	

def Usage():
	print "Usage:"
	print "\t",argv[0],"<ip> <rsu_mib.csv>"
	exit_negative()

def Stats():
	print "No of operations timed out",timeout_errors
	print "No of Invalid value errors",invalid_value
	print "No of failed commits\t",commit_failed
	print "No of out of range values",out_of_range
	stdout.flush()

def check_status(child):
	global timeout_errors
	global exit_flag
	global invalid_value
	global commit_failed
	global out_of_range
	
	print "\n"
	status=child.expect(["[wW]rong","Timeout","commitF","out of range","iso",TIMEOUT,EOF])
	if status==0:
		invalid_value += 1
		system("cat SnmpStatus.txt | grep -A4 -B2 -Ei 'failed|wrong|timeout|commit|out' > SnmpError.txt")
	elif status==1:
		system("cat SnmpStatus.txt | grep -A4 -B2 -Ei 'failed|wrong|timeout|commit|out' > SnmpError.txt")
		timeout_errors += 1
	elif status==2:
		system("cat SnmpStatus.txt | grep -A4 -B2 -Ei 'failed|wrong|timeout|commit|out' > SnmpError.txt")
		commit_failed +=1
	elif status==3:
		system("cat SnmpStatus.txt | grep -A4 -B2 -Ei 'failed|wrong|timeout|commit|out' > SnmpError.txt")
		out_of_range +=1
	elif status!=4:
		print "Expect Timeout"
		system("cat SnmpStatus.txt | grep -A4 -B2 -Ei 'failed|wrong|timeout|commit|out' > SnmpError.txt")
		exit(1)
	sleep(1)
	

try:
	if len(argv)!=3:
		Usage()
	snmpset +=" "+argv[1]
	snmpget +=" "+argv[1]
	mibfile=argv[2]

	
	system("rm -rf ~/.ssh/known*")

	try:
		child=spawn("ssh "+usr+"@localhost")
	except:
		print "Login Failed to localhost",exc_info()
		exit_negative()

	#child.logfile_read=open("SnmpStatus.txt",'w')
	child.logfile_read=stdout
	child.timeout=100

	while True:
		status=child.expect(["[Pp]assword","[yY]es/[nN]o","[yY]/[nN]",EOF,TIMEOUT])
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
			print "Timed Out!!"
			exit_negative()
	status=child.expect(["[pP]ermission","Connect","\$",EOF,TIMEOUT])
	if status==0:
		print "Wrong Password"
		print "Update local username and passwd in the script"
		exit_negative()
	elif status==1:
		print "Connection Refused"
		exit_negative()
	elif status!=2:
		print "Connection Timed out"
		exit_negative()
	
	try:
		fd=open(mibfile,'rb')
	except IOError:
		print "Failed to open the file",exc_info()
		exit_negative()

	for line in fd:
		j=line.split(",")
		field=j[0]
		oid=j[1]
		Type=j[2]


		if Type=="i":
			try:
				min_value=int(j[3])
				max_value=int(j[4])
			except TypeError:
				print "Invalid format. Expecting type \"int\" for field:",field
				exit(1)
			for i in range(0,10): #Set any 10 random integers
				value=randint(min_value-1,max_value+2)
				
				snset=snmpset + " "+oid+" "+Type+" "+" "+str(value)
				print "\n*************************\n"+ field +" "+str (value) +"\n*************************\n"
				child.sendline(snset)
				check_status(child)

				snget=snmpget+" "+oid
				child.sendline(snget)
				check_status(child)
		elif Type=="ip":   #Set an IPv4 and then an IPv6 address
			value=inet_ntoa(pack('>I',randint(0,0xffffffff)))
			snset = snmpset+" "+oid+" s  "+" "+str(value)
			snget = snmpget+" "+oid+" "

			print "\n*************************\n"+ field +" "+str (value) +"\n*************************\n"
			child.sendline(snset)
			check_status(child)

			child.sendline(snget)
			check_status(child)

			value=IPAddress(getrandbits(128))
			snset = snset+" "+oid+" s "+str(value)

			print field
			child.sendline(snset)
			check_status(child)

			child.sendline(snget)
			check_status(child)
		
		elif Type=="s":  #Set any random string of 200B 
			value=''.join(SystemRandom().choice(ascii_uppercase +\
						 digits +ascii_lowercase) for _ in range(200))

			snset=snmpset + " "+oid+" "+Type+" "+str(value)
			print "\n*************************\n"+ field +" "+str (value) +"\n*************************\n"
			child.sendline(snset)
			check_status(child)

			snget=snmpget+" "+oid
			child.sendline(snget)
			check_status(child)
		elif Type=="f":  #Set all the mentioned fixed values in csv file
			for value in j[3].split(":"):
				snset = snmpset + " "+oid+" s "+str(value)
				print "\n*************************\n"+ field +" "+str (value) +"\n*************************\n"
				child.sendline(snset)
				check_status(child)

				snget=snmpget+" "+oid
				child.sendline(snget)
				check_status(child)
		elif Type=="p":
			for i in range(0,10):	#Set any 10 random PSIDs
				value=getRandomPsid()
				snset= snmpset + " "+oid+" s "+str(value)+" "
				print "\n*************************\n"+ field +" "+str (value) +"\n*************************\n"
				child.sendline(snset)
				check_status(child)
		
				snget= snmpget+" "+oid
				child.sendline(snget)
				check_status(child)
		elif Type=="m":			#Set any 10 random MAC addresses
			for i in range(0,10):
				value=getRandomMAC()
				snset= snmpset + " "+oid+" s "+str(value)
				print "\n*************************\n"+ field +" "+str (value) +"\n*************************\n"
				child.sendline(snset)
				check_status(child)
		
				snget= snmpget+" "+oid
				child.sendline(snget)
				check_status(child)
				
		else:
			print "Invalid Type",Type
			exit(1)
		
except KeyboardInterrupt:
	Stats()
	system("cat SnmpStatus.txt | grep -A4 -B2 -Ei 'failed|wrong|timeout|commit|out' > SnmpError.txt")
	exit(0)
except SystemExit:
	if exit_flag:
		exit(1)
	Stats()
	system("cat SnmpStatus.txt | grep -A4 -B2 -Ei 'failed|wrong|timeout|commit|out' > SnmpError.txt")
	exit(0)
except:
	print "Global Exception",exc_info()
	system("cat SnmpStatus.txt | grep -A4 -B2 -Ei 'failed|wrong|timeout|commit|out' > SnmpError.txt")
	stdout.flush()
	exit(1)
