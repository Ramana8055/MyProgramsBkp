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

def config_immediate_forward(master,app):
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

	master.sendline("listenerport "+str(randint(0,65536)))
	sleep(1)
	master.expect("#")

	k = SystemRandom().choice(range(3))
	if k == 0:
		master.sendline("streaming mode disable")
	elif k == 1:
		master.sendline("streaming mode enable receive")
	else:
		master.sendline("streaming mode enable send")
	sleep(1)
        master.expect("#")

	if toggle:
		master.sendline("streaming ip "+str(inet_ntoa(pack('>I',randint(0,0xffffffff)))))
	else:
		master.sendline("streaming ip "+str(IPAddress(getrandbits(128))))
	sleep(1)
        master.expect("#")

        master.sendline("streaming port "+str(randint(0,65536)))
	sleep(1)
        master.expect("#")

	master.sendline("tcdlisten disable") #Add case for enable if TCd is running
	sleep(1)
	master.expect("#")

        master.sendline("security certificate-attachrate "+str(randint(0,5000)))
	sleep(1)
        master.expect("#")

        master.sendline("security generation-location "+SystemRandom().choice(["enable","disable"]))
	sleep(1)
        master.expect("#")

def validate_immediate_forward(master,slave_set,app):
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

	master.sendline("listenerport")
	sleep(1)
	ret = master.expect(["listenerport[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_listenerport = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("streaming mode")
	sleep(1)
	ret = master.expect(["streaming-mode[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_streaming_mode = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("streaming port")
	sleep(1)
	ret = master.expect(["streaming-port[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_streaming_port = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("streaming ip")
	sleep(1)
	ret = master.expect(["streaming-ip[ ]*=[ ]*.*",EOF,TIMEOUT])
	
	if ret == 0:
		master_streaming_ip = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("tcdlisten")
	sleep(1)
	ret = master.expect(["tcdlisten[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_tcdlisten = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("security certificate-attachrate")
	sleep(1)
	ret = master.expect(["certificate-attachrate[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_certattachrate = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("security generation-location")
	sleep(1)
	ret = master.expect(["generation-location[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_gen_loc = master.match.group().split("=")[1].split("\n")[0].lstrip()
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

			slave.sendline("listenerport")
			sleep(1)
			ret = slave.expect(["listenerport[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_listenerport = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_listenerport != slave_listenerport:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("streaming mode")
			sleep(1)
			ret = slave.expect(["streaming-mode[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_streaming_mode = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if slave_streaming_mode != master_streaming_mode:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("streaming port")
			sleep(1)
			ret = slave.expect(["streaming-port[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_streaming_port = slave.match.group().split("=")[1].split("\n")[0].lstrip()
				if slave_streaming_port != master_streaming_port:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("streaming ip")
			sleep(1)
			ret = slave.expect(["streaming-ip[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_streaming_ip = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if slave_streaming_ip != master_streaming_ip:
					Unmatch(slave_id)

			else:
				Slave_down(slave_id)

			slave.sendline("tcdlisten")
			sleep(1)
			ret = slave.expect(["tcdlisten[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_tcdlisten = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if slave_tcdlisten != master_tcdlisten:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)


			slave.sendline("security certificate-attachrate")
			sleep(1)
			ret = slave.expect(["certificate-attachrate[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_certattachrate = slave.match.group().split("=")[1].split("\n")[0].lstrip()
			
				if slave_certattachrate != master_certattachrate:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("security generation-location")
			sleep(1)
			ret = slave.expect(["generation-location[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_gen_loc = slave.match.group().split("=")[1].split("\n")[0].lstrip()
			
				if slave_gen_loc != master_gen_loc:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("exit")
			sleep(1)
			slave.expect("Savari>>")

			slave_id	+= 1
