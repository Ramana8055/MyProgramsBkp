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

def randomMAC():
        mac = [
                randint(0x00, 0xff),
                randint(0x00, 0xff),
                randint(0x00, 0xff),
                randint(0x00, 0xff),
                randint(0x00, 0xff),
                randint(0x00, 0xff) ]
        return ':'.join(map(lambda x: "%02x" % x, mac))

def Master_down():
	print "Mater is Down"
	exit(1)

def Slave_down(Slave_id):
	print "Slave with id:",Slave_id,"is down"
	exit(1)

def Unmatch(slave_id):
	print "Configuration is not affected in slave id:",slave_id
	exit(1)

def config_ipv6_provider(master,app):
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

	master.sendline("wsa psid "+str(hex(randint(0x00,0xffffffff))))
	sleep(1)
	master.expect("#")

	master.sendline("wsa security "+SystemRandom().choice(["enable","disable"]))
	sleep(1)
	master.expect("#")

	master.sendline("wsa priority "+str(randint(0,64)))
	sleep(1)
	master.expect("#")

	master.sendline("wsa advertiser-id "+SystemRandom().choice(["NULL",
		''.join(SystemRandom().choice(ascii_uppercase+ascii_lowercase+digits) for _ in range(31))]) )
	sleep(1)
	master.expect("#")

	master.sendline("wsa service-context "+SystemRandom().choice(["NULL",
		''.join(SystemRandom().choice(ascii_uppercase+ascii_lowercase+digits) for _ in range(31))]) )
	sleep(1)
	master.expect("#")

	master.sendline("wsa ipv6addr "+SystemRandom().choice(["NULL",str(IPAddress(getrandbits(128)))]))
	sleep(1)
        master.expect("#")

        master.sendline("wsa port "+str(randint(0,65536)))
	sleep(1)
        master.expect("#")

	master.sendline("wsa macaddr "+SystemRandom().choice(["NULL",str(randomMAC())]))
	sleep(1)
	master.expect("#")

	master.sendline("wsa repeat-rate "+str(randint(0,255)))
	sleep(1)
	master.expect("#")

	master.sendline("wra lifetime "+str(randint(0,65536)))
	sleep(1)
	master.expect("#")

	master.sendline("wra prefix "+str(":".join( SystemRandom().choice( [hex(randint(0,0xffff))] ).split("0x")[1]  
					for _ in range(4)))+"::")
	sleep(1)
	master.expect("#")

	master.sendline("wra prefixlen "+str(randint(0,128)))
	sleep(1)
	master.expect("#")

	master.sendline("wra gateway-address ipv6 "+SystemRandom().choice(["NULL",str(IPAddress(getrandbits(128)))]))
	sleep(1)
        master.expect("#")

	master.sendline("wra gateway-address mac "+SystemRandom().choice(["NULL",str(randomMAC())]))
	sleep(1)
	master.expect("#")

	master.sendline("wra dns primary "+SystemRandom().choice(["NULL",str(IPAddress(getrandbits(128)))]))
	sleep(1)
        master.expect("#")

def validate_ipv6_provider(master,slave_set,app):
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

	master.sendline("wsa psid")
	sleep(1)
	ret = master.expect(["psid[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wsa_psid = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wsa security")
	sleep(1)
	ret = master.expect(["security[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wsa_security = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wsa priority")
	sleep(1)
	ret = master.expect(["priority[ ]*=[ ]*.*",EOF,TIMEOUT])
	
	if ret == 0:
		master_wsa_priority = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wsa advertiser-id")
	sleep(1)
	ret = master.expect(["advertiser-id[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wsa_advertiser_id = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wsa service-context")
	sleep(1)
	ret = master.expect(["service-context[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wsa_service_context = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wsa ipv6addr")
	sleep(1)
	ret = master.expect(["ipv6ddr[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wsa_ipv6addr = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wsa port")
	sleep(1)
	ret = master.expect(["port[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wsa_port = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wsa provider-macaddr")
	sleep(1)
	ret = master.expect(["macddress[ ]*=[ ]*.*",EOF,TIMEOUT]) #Modify if the spelling changes for "macddress"

	if ret == 0:
		master_wsa_mac = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wsa repeat-rate")
	sleep(1)
	ret = master.expect(["repeat-rate[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wsa_repeat_rate = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wra lifetime")
	sleep(1)
	ret = master.expect(["lifetime[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wra_lifetime = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wra prefix")
	sleep(1)
	ret = master.expect(["prefix[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wra_prefix = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wra prefixlen")
	sleep(1)
	ret = master.expect(["prefixlen[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wra_prefixlen = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wra gateway-address ipv6")
	sleep(1)
	ret = master.expect(["gateway-ipv6[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wra_gateway_ipv6 = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wra gateway-address mac")
	sleep(1)
	ret = master.expect(["gateway-mac[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wra_gateway_mac = master.match.group().split("=")[1].split("\n")[0].lstrip()
	else:
		Master_down()

	master.sendline("wra dns primary")
	sleep(1)
	ret = master.expect(["primary-dns[ ]*=[ ]*.*",EOF,TIMEOUT])

	if ret == 0:
		master_wra_primary_dns = master.match.group().split("=")[1].split("\n")[0].lstrip()
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

			
			slave.sendline("wsa psid")
			sleep(1)
			ret = slave.expect(["psid[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wsa_psid = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wsa_psid != slave_wsa_psid:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wsa security")
			sleep(1)
			ret = slave.expect(["security[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wsa_security = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wsa_security != slave_wsa_security:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wsa priority")
			sleep(1)
			ret = slave.expect(["priority[ ]*=[ ]*.*",EOF,TIMEOUT])
	
			if ret == 0:
				slave_wsa_priority = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wsa_priority != slave_wsa_priority:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wsa advertiser-id")
			sleep(1)
			ret = slave.expect(["advertiser-id[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wsa_advertiser_id = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wsa_advertiser_id != slave_wsa_advertiser_id:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wsa service-context")
			sleep(1)
			ret = slave.expect(["service-context[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wsa_service_context = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wsa_service_context != slave_wsa_service_context:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wsa ipv6addr")
			sleep(1)
			ret = slave.expect(["ipv6ddr[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wsa_ipv6addr = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wsa_ipv6addr != slave_wsa_ipv6addr:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wsa port")
			sleep(1)
			ret = slave.expect(["port[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wsa_port = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wsa_port != slave_wsa_port:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wsa provider-macaddr")
			sleep(1)
			ret = slave.expect(["macddress[ ]*=[ ]*.*",EOF,TIMEOUT]) #Modify if the spelling changes for "macddress"

			if ret == 0:
				slave_wsa_mac = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wsa_mac != slave_wsa_mac:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wsa repeat-rate")
			sleep(1)
			ret = slave.expect(["repeat-rate[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wsa_repeat_rate = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wsa_repeat_rate != slave_wsa_repeat_rate:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wra lifetime")
			sleep(1)
			ret = slave.expect(["lifetime[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wra_lifetime = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wra_lifetime != slave_wra_lifetime:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wra prefix")
			sleep(1)
			ret = slave.expect(["prefix[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wra_prefix = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wra_prefix != slave_wra_prefix:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wra prefixlen")
			sleep(1)
			ret = slave.expect(["prefixlen[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wra_prefixlen = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wra_prefixlen != slave_wra_prefixlen:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wra gateway-address ipv6")
			sleep(1)
			ret = slave.expect(["gateway-ipv6[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wra_gateway_ipv6 = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wra_gateway_ipv6 != slave_wra_gateway_ipv6:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wra gateway-address mac")
			sleep(1)
			ret = slave.expect(["gateway-mac[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wra_gateway_mac = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wra_gateway_mac != slave_wra_gateway_mac:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)

			slave.sendline("wra dns primary")
			sleep(1)
			ret = slave.expect(["primary-dns[ ]*=[ ]*.*",EOF,TIMEOUT])

			if ret == 0:
				slave_wra_primary_dns = slave.match.group().split("=")[1].split("\n")[0].lstrip()

				if master_wra_primary_dns != slave_wra_primary_dns:
					Unmatch(slave_id)
			else:
				Slave_down(slave_id)


			slave.sendline("exit")
			sleep(1)
			slave.expect("Savari>>")

			slave_id	+= 1
