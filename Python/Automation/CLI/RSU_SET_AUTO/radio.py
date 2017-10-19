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

def config_radio(master,app):
	global toggle
	toggle	= not toggle

        master.sendline("config app "+app)
	sleep(1)
        ret=master.expect(["[cC]ommand","[iI]nvalid","#",TIMEOUT,EOF])
        if ret!=2:
                print "Invalid command"
                stdout.flush()
                exit(1)

	master.sendline("dsrc0 chan_mode "+str(SystemRandom().choice([0,1])))
	sleep(1)
        master.expect("#")

	master.sendline("dsrc1 chan_mode "+str(SystemRandom().choice([0,1])))
	sleep(1)
        master.expect("#")

        master.sendline("dsrc0 svc "+str(randint(172,184)))
	sleep(1)
        master.expect("#")

        master.sendline("dsrc1 svc "+str(randint(172,184)))
	sleep(1)
        master.expect("#")

def validate_radio(master,slave_set,app):
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

	master.sendline("dsrc0 chan_mode")
	sleep(1)
	ret = master.expect(["dsrc0 channel mode[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_dsrc0_chmode = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("dsrc1 chan_mode")
	sleep(1)
	ret = master.expect(["dsrc1 channel mode[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_dsrc1_chmode = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("dsrc0 cch")
	sleep(1)
	ret = master.expect(["dsrc0 control channel[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_dsrc0_cch = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("dsrc1 cch")
	sleep(1)
	ret = master.expect(["dsrc1 control channel[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_dsrc1_cch = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("dsrc0 svc")
	sleep(1)
	ret = master.expect(["dsrc0 service channel[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_dsrc0_svc = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("dsrc1 svc")
	sleep(1)
	ret = master.expect(["dsrc1 service channel[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_dsrc1_svc = master.match.group().split("=")[1].split("\n")[0].lstrip()
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

			slave.sendline("dsrc0 chan_mode")
			sleep(1)
			ret = slave.expect(["dsrc0 channel mode[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_dsrc0_chmode = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_dsrc0_chmode != slave_dsrc0_chmode:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("dsrc1 chan_mode")
			sleep(1)
			ret = slave.expect(["dsrc1 channel mode[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_dsrc1_chmode = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_dsrc1_chmode != slave_dsrc1_chmode:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("dsrc0 cch")
			sleep(1)
			ret = slave.expect(["dsrc0 control channel[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_dsrc0_cch = slave.match.group().split("=")[1].split("\n")[0].lstrip()
				if slave_dsrc0_cch != master_dsrc0_cch:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("dsrc1 cch")
			sleep(1)
			ret = slave.expect(["dsrc1 control channel[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_dsrc1_cch = slave.match.group().split("=")[1].split("\n")[0].lstrip()
				if slave_dsrc1_cch != master_dsrc1_cch:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("dsrc0 svc")
			sleep(1)
			ret = slave.expect(["dsrc0 service channel[ ]*=[ ]*.*",EOF,TIMEOUT])
			
			if ret == 0:
				slave_dsrc0_svc = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if slave_dsrc0_svc != master_dsrc0_svc:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("dsrc1 svc")
			sleep(1)
			ret = slave.expect(["dsrc1 service channel[ ]*=[ ]*.*",EOF,TIMEOUT])
			
			if ret == 0:
				slave_dsrc1_svc = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if slave_dsrc1_svc != master_dsrc1_svc:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("exit")
			sleep(1)
			slave.expect("Savari>>")

			slave_id	+= 1
