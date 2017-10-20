from pexpect import EOF,TIMEOUT
from sys import stdout,exit
from os import system
from struct import pack
from random import randint,getrandbits,SystemRandom
from time import time,sleep
from socket import inet_ntoa
from netaddr.ip import IPAddress,IPNetwork

toggle = True
def Master_down():
	print "Mater is Down"
	exit(1)

def Slave_down(Slave_id):
	print "Slave with id:",Slave_id,"is down"
	exit(1)

def Unmatch(slave_id):
	print "Configuration is not affected in slave id:",slave_id
	exit(1)

def config_gpsoutput(master,app):
	global toggle
	toggle	= not toggle

        master.sendline("config app "+app)
	sleep(1)
        ret=master.expect(["[cC]ommand","[iI]nvalid","#",TIMEOUT,EOF])
        if ret!=2:
                print "Invalid command"
                stdout.flush()
                exit(1)

	if toggle:
		master.sendline("enable")
	else:
		master.sendline("disable")
	sleep(1)
        master.expect("#")

        master.sendline("port "+str(randint(0,65536)))
	sleep(1)
        master.expect("#")

	master.sendline("sample-rate "+str(randint(0,18000)))
	sleep(1)
	master.expect("#")

def validate_gpsoutput(master,slave_set,app):
	master.sendline("commit")

	ret = master.expect(["[Oo]peration [fF]ailed","[wW]rite [oO]peration","[rR]ead [oO]peration",
					"[bB]roken [pP]ipe","[Tt]imed [oO]ut","#",EOF,TIMEOUT])

	if ret == 0:
		print "Operation Failed"
		exit(1)
	elif ret == 1:
		print "Write Operation Failed"
		exit(1)
	elif ret == 2:
		print "Read Operation Failed"
		exit(1)
	elif ret == 3:
		print "Broken Pipe"
		exit(1)
	elif ret == 4:
		print "Operation Timedout"
		exit(1)
	elif ret == 6:
		print "Master is Down, EOF reached"
		exit(1)
	elif ret == 7:
		print "Expect Timeout"
		exit(1)


	master.sendline("exit")
	master.expect("Savari>>")

	master.sendline("show app "+app)
	sleep(1)
	master.expect("#")	

	master.sendline("status")
	sleep(1)
	ret = master.expect(["status[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_status = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("port")
	sleep(1)
	ret = master.expect(["port[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_port = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("sample-rate")
	sleep(1)
	ret = master.expect(["sample-rate[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_sample_rate = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("exit")
	master.expect("Savari>>")

	master.sendline("show system date")
	master.expect("Savari>>")

	slave_id = 1
	for slave in slave_set:
			slave.sendline("show app "+app)
			sleep(1)
			slave.expect("#")

			slave.sendline("status")
			sleep(1)
			ret = slave.expect(["status[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_status = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_status != slave_status:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("port")
			sleep(1)
			ret = slave.expect(["port[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_port = slave.match.group().split("=")[1].split("\n")[0].lstrip()
				if slave_port != master_port:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("sample-rate")
			sleep(1)
			ret = slave.expect(["sample-rate[ ]*=[ ]*.*",EOF,TIMEOUT])
			
			if ret == 0:
				slave_sample_rate = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if slave_sample_rate != master_sample_rate:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("exit")
			sleep(1)
			slave.expect("Savari>>")

			slave_id	+= 1