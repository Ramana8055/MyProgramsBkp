from pexpect import EOF,TIMEOUT
from sys import stdout,exit
from os import system
from struct import pack
from random import randint,getrandbits,SystemRandom
from time import time,sleep
from socket import inet_ntoa
from netaddr.ip import IPAddress,IPNetwork
from string import ascii_uppercase,ascii_lowercase,digits
toggle = True

psidlist = []

def randPSID():
	return hex(SystemRandom().choice([randint(0x0,0x7f),randint(0x8000,0xbfff)]))

def Master_down():
	print "Master is Down"
	exit(1)

def Slave_down(Slave_id):
	print "Slave with id:",Slave_id,"is down"
	exit(1)

def Unmatch(slave_id):
	print "Configuration is not affected in slave id:",slave_id
	exit(1)

def delete_all_psids(master):
        while True:
                master.sendline("review")
                master.expect("[pP]sid[ ]*=[ ]*0x[a-fA-F0-9]*")
                master.sendline("delete "+master.match.group().split("=")[1].split("\n")[0])
                sleep(1)
                status=master.expect(["Cannot delete",TIMEOUT],3) 
                if status==0:
                        break
                elif status==1:
                        pass
                master.expect("#")
                stdout.flush()

def config_dsrc_message_forward(master,slave_set,app):
	global toggle,psidlist
	toggle	= not toggle

        master.sendline("config app "+app)
	sleep(1)
        ret=master.expect(["[cC]ommand","[iI]nvalid","#",TIMEOUT,EOF])
        if ret!=2:
                print "Invalid command"
                stdout.flush()
                exit(1)

	delete_all_psids(master)	
	#validate_dsrc_message_forward(master,slave_set,app)

	print "Deletion Successful\n"

	psidlist[:] = []

	for psid_no in range(9): #Since one psid is already present
		psidlist.append(str(randPSID()))

	if toggle:
		master.sendline("enable")
	else:
		master.sendline("disable")
	sleep(1)
        master.expect("#")

	master.sendline("rsu-id "+str(randint(0,4294967295)))
	master.expect("#")

	for psid in psidlist:
		master.sendline("psid "+psid)
		sleep(1)
		master.expect("#")

		master.sendline("rssi "+str(randint(-100,-60)))
		sleep(1)
		master.expect("#")

		master.sendline("message-interval "+str(randint(1,9)))
		master.expect("#")

		master.sendline("delivery-time start NULL")
		master.expect("#")

		master.sendline("delivery-time stop NULL")
		master.expect("#")

		master.sendline("infusion-header "+str(SystemRandom().choice(["enable","disable"])))
		master.expect("#")

		master.sendline("infusion-msgtype "+str(randint(0,255)))
		master.expect("#")

		master.sendline("destination ip "+\
			SystemRandom().choice([str(inet_ntoa(pack('>I',randint(0,0xffffffff)))),
								str(IPAddress(getrandbits(128)))]))
		master.expect("#")

		master.sendline("destination protocol "+SystemRandom().choice(["UDP","TCP"]))
		master.expect("#")

		master.sendline("destination port "+str(randint(1024,65535)))
		master.expect("#")

		master.sendline("exit")
		master.expect("#")

def validate_dsrc_message_forward(master,slave_set,app):
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

	master.sendline("rsu-id")
	sleep(1)
	ret = master.expect(["rsu-id[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_rsu_id = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("psid")
	p=1
	psid_list_master = []
	while True:
		ret = master.expect(["psid"+str(p)+"[ ]*=[ ]*.*",EOF,TIMEOUT],10)
		if ret == 0:
			psid_list_master.append(master.match.group().split("=")[1].split("\n")[0].lstrip())
		elif ret == 1:
			Master_down()
		else:
			break
		p += 1

	slave_id = 1
	for slave in slave_set:
		slave.sendline("show app "+app)
		sleep(1)
		slave.expect("#")

		slave.sendline("psid")
		p = 1
		psid_list_slave = []
		while True:
			ret = slave.expect(["psid"+str(p)+"[ ]*=[ ]*.*",EOF,TIMEOUT],10)
			if ret == 0:
				psid_list_slave.append(slave.match.group().split("=")[1].split("\n")[0].lstrip())
			elif ret == 1:
				Slave_down(slave_id)
			else:
				break
			p += 1

		if cmp(psid_list_master,psid_list_master) != 0:
			print "List of PSIDs are diffrent in master and in slave with slave_id:",slave_id
			exit(1)
		
		slave.sendline("exit")
		slave.expect("Savari>>")

		slave_id += 1

	master_rssi_list 	= []
	master_msg_int_list 	= []
	master_del_start_list	= []
	master_del_stop_list	= []
	master_inf_head_list	= []
	master_inf_msg_type_list= []
	master_dest_proto_list	= []
	master_dest_port_list	= []
	master_dest_ip_list	= []

	for psid in psid_list_master:
		master.sendline("psid "+psid)
		master.expect("#")

		master.sendline("rssi")
		ret = master.expect(["rssi[ ]*=[ ]*.*",EOF,TIMEOUT])

		if ret == 0:
			master_rssi_list.append(master.match.group().split("=")[1].split("\n")[0].lstrip())
		else:
			Master_down()

		master.sendline("message-interval")
		ret = master.expect(["message-interval[ ]*=[ ]*.*",EOF,TIMEOUT])

		if ret == 0:
			master_msg_int_list.append(master.match.group().split("=")[1].split("\n")[0].lstrip())
		else:
			Master_down()

		master.sendline("delivery start-time")
		ret = master.expect(["start-time[ ]*=[ ]*.*",EOF,TIMEOUT])

		if ret == 0:
			master_del_start_list.append(master.match.group().split("=")[1].split("\n")[0].lstrip())
		else:
			Master_down()

		master.sendline("delivery stop-time")
		ret = master.expect(["stop-time[ ]*=[ ]*.*",EOF,TIMEOUT])

		if ret == 0:
			master_del_start_list.append(master.match.group().split("=")[1].split("\n")[0].lstrip())
		else:
			Master_down()

		master.sendline("infusion-header")
		ret = master.expect(["infusion-header[ ]*=[ ]*.*",EOF,TIMEOUT])

		if ret == 0:
			master_inf_head_list.append(master.match.group().split("=")[1].split("\n")[0].lstrip())
		else:
			Master_down()

		master.sendline("infusion-msgtype")
		ret = master.expect(["infusion-msgtype[ ]*=[ ]*.*",EOF,TIMEOUT])
			
		if ret == 0:
			master_inf_head_list.append(master.match.group().split("=")[1].split("\n")[0].lstrip())
		else:
			Master_down()

		master.sendline("destination protocol")
		ret = master.expect(["destination-protocol[ ]*=[ ]*.*",EOF,TIMEOUT])

		if ret == 0:
			master_dest_proto_list.append(master.match.group().split("=")[1].split("\n")[0].lstrip())
		else:
			Master_down()

		master.sendline("destination port")
		ret = master.expect(["destination-port[ ]*=[ ]*.*",EOF,TIMEOUT])

		if ret == 0:
			master_dest_port_list.append(master.match.group().split("=")[1].split("\n")[0].lstrip())
		else:
			Master_down()

		master.sendline("destination ip")
		ret = master.expect(["destination-ip[ ]*=[ ]*.*",EOF,TIMEOUT])

		if ret == 0:
			master_dest_ip_list.append(master.match.group().split("=")[1].split("\n")[0].lstrip())
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

		slave.sendline("rsu-id")
		sleep(1)
		ret = slave.expect(["rsu-id[ ]*=[ ]*.*",EOF,TIMEOUT])

		if ret == 0:
			slave_rsu_id = slave.match.group().split("=")[1].split("\n")[0].lstrip()

			if master_rsu_id != slave_rsu_id:
				Unmatch(slave_id)
		else:
			Slave_down(slave_id) 

		slave_rssi_list 	= []
		slave_msg_int_list 	= []
		slave_del_start_list	= []
		slave_del_stop_list	= []
		slave_inf_head_list	= []
		slave_inf_msg_type_list= []
		slave_dest_proto_list	= []
		slave_dest_port_list	= []
		slave_dest_ip_list	= []

		for psid in psid_list_slave:
			slave.sendline("psid "+psid)
			slave.expect("#")

			mslave.sendline("rssi")
			ret = slave.expect(["rssi[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_rssi_list.append(slave.match.group().split("=")[1].split("\n")[0].lstrip())
			else:
				Slave_down(slave_id)

			slave.sendline("message-interval")
			ret = slave.expect(["message-interval[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_msg_int_list.append(slave.match.group().split("=")[1].split("\n")[0].lstrip())
			else:
				Slave_down(slave_id)

			slave.sendline("delivery start-time")
			ret = slave.expect(["start-time[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_del_start_list.append(slave.match.group().split("=")[1].split("\n")[0].lstrip())
			else:
				Slave_down(slave_id)

			slave.sendline("delivery stop-time")
			ret = slave.expect(["stop-time[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_del_start_list.append(slave.match.group().split("=")[1].split("\n")[0].lstrip())
			else:
				Slave_down(slave_id)

			slave.sendline("infusion-header")
			ret = slave.expect(["infusion-header[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_inf_head_list.append(slave.match.group().split("=")[1].split("\n")[0].lstrip())
			else:
				Slave_down(slave_id)

			slave.sendline("infusion-msgtype")
			ret = slave.expect(["infusion-msgtype[ ]*=[ ]*.*",EOF,TIMEOUT])
			
			if ret == 0:
				slave_inf_head_list.append(slave.match.group().split("=")[1].split("\n")[0].lstrip())
			else:
				Slave_down(slave_id)

			slave.sendline("destination protocol")
			ret = slave.expect(["destination-protocol[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_dest_proto_list.append(slave.match.group().split("=")[1].split("\n")[0].lstrip())
			else:
				Slave_down(slave_id)

			slave.sendline("destination port")
			ret = slave.expect(["destination-port[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_dest_port_list.append(slave.match.group().split("=")[1].split("\n")[0].lstrip())
			else:
				Slave_down(slave_id)

			slave.sendline("destination ip")
			ret = slave.expect(["destination-ip[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_dest_ip_list.append(slave.match.group().split("=")[1].split("\n")[0].lstrip())
			else:
				Slave_down(slave_id)

		if cmp(master_rssi_list, slave_rssi_list) != 0:
			print "RSSI missmatch"
			Unmatch(slave_id)
		if cmp(master_msg_int_list,slave_msg_int_list) != 0:
			print "Msg-Interval missmatch"
			Unmatch(slave_id)
		if cmp(master_del_start_list,slave_del_start_list) != 0:
			print "delivery start time missmatch"
			Unmatch(slave_id)
		if cmp(master_del_stop_list,slave_del_stop_list) != 0:
			print "Delivery stop time missmatch"
			Unmatch(slave_id)
		if cmp(master_inf_head_list,slave_inf_head_list) != 0:
			print "Infusion Header missmatch"
			Unmatch(slave_id)
		if cmp(master_inf_msg_type_list,slave_inf_msg_type_list) != 0:
			print "Infusion msg type missmatch"
			Unmatch(slave_id)
		if cmp(master_dest_proto_list,slave_dest_proto_list) != 0:
			print "Destination Protocol missmatch"
			Unmatch(slave_id)
		if cmp(master_dest_port_list,slave_dest_port_list) != 0:
			print "Destination Port Missmatch"
			Unmatch(slave_id)
		if cmp(master_dest_ip_list,slave_dest_ip_list) != 0:
			print "Destination ip missmatch"
			Unmatch(slave_id)
			
		slave.sendline("exit")
		sleep(1)
		slave.expect("#")

		slave.sendline("exit")
		sleep(1)
		slave.expect("Savari>>")

		slave_id	+= 1
