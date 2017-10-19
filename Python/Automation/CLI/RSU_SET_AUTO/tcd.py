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
def Master_down():
	print "Mater is Down"
	exit(1)

def Slave_down(Slave_id):
	print "Slave with id:",Slave_id,"is down"
	exit(1)

def Unmatch(slave_id):
	print "Configuration is not affected in slave id:",slave_id
	exit(1)

def config_tcd(master,app):
	global toggle

	master.sendline("enable privileged-mode")
	master.expect("Enter password")

	master.sendline('6efre#ESpe')
	ret = master.expect(["Enter privileged mode","Savari"])
	if ret != 0:
		print "Privilege mode password incorrect"
		exit(1)

	if toggle:

		mode = str(SystemRandom().choice(["ntcip","immediate-forward","broadcast"]))

		master.sendline("config system j2735 2015")
		master.expect("Savari>>")

		master.sendline("config app "+app+" ntcip mapfile Sample_RLVW_8_lane_MAP.xml") #Change this accordingly
		master.expect("Savari>>")

		master.sendline("config app "+app+" mode "+mode)
		master.expect("Savari>>")
	else:
		mode = str(SystemRandom().choice(["ntcip","immediate-forward"]))

		master.sendline("config system j2735 2009")
		master.expect("Savari>>")

		master.sendline("config app "+app+" ntcip mapfile sample.rndf") #Change this accordingly
		master.expect("Savari>>")

		master.sendline("config app "+app+" mode "+mode)
		master.expect("Savari>>")
			
	master.sendline("disable privileged-mode")
	master.expect("Savari>>")

        master.sendline("config app "+app)
	sleep(1)
        ret=master.expect(["[cC]ommand","[iI]nvalid","#",TIMEOUT,EOF])
        if ret!=2:
                print "Invalid command"
                stdout.flush()
                exit_flag = 1
                exit(1)

	master.sendline(SystemRandom().choice(["enable","disable"]))
	sleep(1)
        master.expect("#")

	master.sendline("ntcip tc-ipaddr "+str(SystemRandom().choice([inet_ntoa(pack('>I',randint(0,0xffffffff))),
											IPAddress(getrandbits(128))])))
	sleep(1)
	master.expect("#")

	master.sendline("ntcip tc-port "+str(randint(0,655336)))
	sleep(1)
	master.expect("#")

	#Add case for TC-Type if Supported

	master.sendline("ntcip spat-tx-intvl "+str(randint(100,2000)))
	sleep(1)
	master.expect("#")

	master.sendline("ntcip map-tx-intvl "+str(randint(1,10000)))
	sleep(1)
	master.expect("#")

	master.sendline("ntcip send-red-states "+SystemRandom().choice(["enable","disable"]))
	sleep(1)
	master.expect("#")

	master.sendline("ntcip detector-info "+SystemRandom().choice(["enable","disable"]))
	sleep(1)
        master.expect("#")

        master.sendline("broadcast port "+str(randint(0,65536)))
	sleep(1)
        master.expect("#")

        master.sendline("immediate-forward port "+str(randint(0,65536)))
	sleep(1)
        master.expect("#")

	master.sendline("spat psid "+str(hex(randint(0x00,0xffffffff))))
	sleep(1)
	master.expect("#")

        master.sendline("spat priority "+str(randint(0,63)))
	sleep(1)
        master.expect("#")

	master.sendline("spat signature "+SystemRandom().choice(["True","False"]))
	sleep(1)
	master.expect("#")

	master.sendline("spat encryption "+SystemRandom().choice(["True","False"]))
	sleep(1)
	master.expect("#")

	master.sendline("spat transmit-enabled-lanes "+SystemRandom().choice(["enable","disable"]))
	sleep(1)
	master.expect("#")

        master.sendline("spat certificate-attachrate  "+str(randint(500,10000)))
	sleep(1)
        master.expect("#")

	master.sendline("spat certificate-optimisation "+SystemRandom().choice(["enable","disable"]))
	sleep(1)
        master.expect("#")

	master.sendline("map psid "+str(hex(randint(0x00,0xffffffff))))
	sleep(1)
	master.expect("#")

        master.sendline("map priority "+str(randint(0,63)))
	sleep(1)
        master.expect("#")

	master.sendline("map signature "+SystemRandom().choice(["True","False"]))
	sleep(1)
	master.expect("#")

	master.sendline("map encryption "+SystemRandom().choice(["True","False"]))
	sleep(1)
	master.expect("#")

        master.sendline("map persistent-timeout  "+str(randint(1,1440)))
	sleep(1)
        master.expect("#")

        master.sendline("map certificate-attachrate  "+str(randint(1000,10000)))
	sleep(1)
        master.expect("#")

def validate_tcd(master,slave_set,app):
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

	master.sendline("mode")
	sleep(1)
	ret = master.expect(["mode[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_mode = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("ntcip tc-ipaddr")
	sleep(1)
	ret = master.expect(["tc-ipaddr[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_tc_ipaddr = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("ntcip tc-port")
	sleep(1)
	ret = master.expect(["tc-port[ ]*=[ ]*.*",EOF,TIMEOUT])
	
	if ret == 0:
		master_tc_port = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("ntcip tc-type")
	sleep(1)
	ret = master.expect(["tc-type[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_tc_type = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("ntcip spat-tx-intvl")
	sleep(1)
	ret = master.expect(["spat-tx-intvl[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_spat_tx_intvl = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("ntcip map-tx-intvl")
	sleep(1)
	ret = master.expect(["map-tx-intvl[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_map_tx_intvl = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("ntcip send-red-states status")
	sleep(1)
	ret = master.expect(["send-red-states[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_send_red_states = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("ntcip detector-info status")
	sleep(1)
	ret = master.expect(["detector-info[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_detector_info = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("ntcip mapfile")
	sleep(1)
	ret = master.expect(["mapfile[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_mapfile = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("broadcast port")
	sleep(1)
	ret = master.expect(["broadcast-port[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_broadcast_port = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("immediate-forward port")
	sleep(1)
	ret = master.expect(["immediate-forward-port[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_immediate_forward_port = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("spat psid")
	sleep(1)
	ret = master.expect(["spat-psid[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_spat_psid = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("spat priority")
	sleep(1)
	ret = master.expect(["spat-priority[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_spat_priority = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("spat signature")
	sleep(1)
	ret = master.expect(["spat-signature[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_spat_signature = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("spat encryption")
	sleep(1)
	ret = master.expect(["spat-encryption[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_spat_encryption = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("spat transmit-enabled-lanes status")
	sleep(1)
	ret = master.expect(["transmit-enabled-lanes[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_transmit_enabled_lanes = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("spat certificate-attachrate")
	sleep(1)
	ret = master.expect(["spat-certificate-attachrate[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_spat_certificate_attachrate = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("spat certificate-optimisation status")
	sleep(1)
	ret = master.expect(["certificate-optimisation[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_certificate_optimisation = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("map psid")
	sleep(1)
	ret = master.expect(["map-psid[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_map_psid = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("map priority")
	sleep(1)
	ret = master.expect(["map-priority[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_map_priority = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("map signature")
	sleep(1)
	ret = master.expect(["map-signature[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_map_signature = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("map encryption")
	sleep(1)
	ret = master.expect(["map-encryption[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_map_encryption = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("map persistent-timeout")
	sleep(1)
	ret = master.expect(["map-persistent-timeout[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_map_persistent_timeout = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("map certificate-attachrate")
	sleep(1)
	ret = master.expect(["map-certAttachRate[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_map_certAttachRate = master.match.group().split("=")[1].split("\n")[0].lstrip()
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

			
			slave.sendline("mode")
			sleep(1)
			ret = slave.expect(["mode[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_mode = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_mode != slave_mode:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("ntcip tc-ipaddr")
			sleep(1)
			ret = slave.expect(["tc-ipaddr[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_tc_ipaddr = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_tc_ipaddr != slave_tc_ipaddr:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("ntcip tc-port")
			sleep(1)
			ret = slave.expect(["tc-port[ ]*=[ ]*.*",EOF,TIMEOUT])
	
			if ret == 0:
				slave_tc_port = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_tc_port != slave_tc_port:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("ntcip tc-type")
			sleep(1)
			ret = slave.expect(["tc-type[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_tc_type = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_tc_type != slave_tc_type:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("ntcip spat-tx-intvl")
			sleep(1)
			ret = slave.expect(["spat-tx-intvl[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_spat_tx_intvl = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_spat_tx_intvl != slave_spat_tx_intvl:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("ntcip map-tx-intvl")
			sleep(1)
			ret = slave.expect(["map-tx-intvl[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_map_tx_intvl = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_map_tx_intvl != slave_map_tx_intvl:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("ntcip send-red-states status")
			sleep(1)
			ret = slave.expect(["send-red-states[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_send_red_states = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_send_red_states != slave_send_red_states:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("ntcip detector-info status")
			sleep(1)
			ret = slave.expect(["detector-info[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_detector_info = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_detector_info != slave_send_red_states:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("ntcip mapfile")
			sleep(1)
			ret = slave.expect(["mapfile[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_mapfile = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_mapfile != slave_mapfile:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("broadcast port")
			sleep(1)
			ret = slave.expect(["broadcast-port[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_broadcast_port = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_broadcast_port != slave_broadcast_port:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("immediate-forward port")
			sleep(1)
			ret = slave.expect(["immediate-forward-port[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_immediate_forward_port = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_immediate_forward_port != slave_immediate_forward_port:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("spat psid")
			sleep(1)
			ret = slave.expect(["spat-psid[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_spat_psid = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_spat_psid != slave_spat_psid:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("spat priority")
			sleep(1)
			ret = slave.expect(["spat-priority[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_spat_priority = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_spat_priority != slave_spat_priority:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("spat signature")
			sleep(1)
			ret = slave.expect(["spat-signature[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_spat_signature = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_spat_signature != slave_spat_signature:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("spat encryption")
			sleep(1)
			ret = slave.expect(["spat-encryption[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_spat_encryption = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_spat_encryption != slave_spat_encryption:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("spat transmit-enabled-lanes status")
			sleep(1)
			ret = slave.expect(["transmit-enabled-lanes[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_transmit_enabled_lanes = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_transmit_enabled_lanes != slave_transmit_enabled_lanes:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("spat certificate-attachrate")
			sleep(1)
			ret = slave.expect(["spat-certificate-attachrate[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_spat_certificate_attachrate = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_spat_certificate_attachrate != slave_spat_certificate_attachrate:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("spat certificate-optimisation status")
			sleep(1)
			ret = slave.expect(["certificate-optimisation[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_certificate_optimisation = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_certificate_optimisation != slave_certificate_optimisation:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("map psid")
			sleep(1)
			ret = slave.expect(["map-psid[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_map_psid = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_map_psid != slave_map_psid:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("map priority")
			sleep(1)
			ret = slave.expect(["map-priority[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_map_priority = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_map_priority != slave_map_priority:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("map signature")
			sleep(1)
			ret = slave.expect(["map-signature[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_map_signature = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_map_signature != slave_map_signature:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("map encryption")
			sleep(1)
			ret = slave.expect(["map-encryption[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_map_encryption = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_map_encryption != slave_map_encryption:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("map persistent-timeout")
			sleep(1)
			ret = slave.expect(["map-persistent-timeout[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_map_persistent_timeout = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_map_persistent_timeout != slave_map_persistent_timeout:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("map certificate-attachrate")
			sleep(1)
			ret = slave.expect(["map-certAttachRate[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_map_certAttachRate = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_map_certAttachRate != slave_map_certAttachRate:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("exit")
			sleep(1)
			slave.expect("Savari>>")

			slave_id	+= 1
