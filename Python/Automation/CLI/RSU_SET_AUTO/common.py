#!/usr/bin/python -B
from pexpect import spawn,TIMEOUT,EOF
from sys import stdout,exit,exc_info,argv
from time import time,sleep

Timeout		= 100
passwd		= ""
toggle		= True

apps=["ipv6-provider","immediate-forward","dsrc-message-forward","bsmforwd","wsmpforwd","store-repeat","tcd","gpsoutput","radio"]

sshcmd		= "ssh -p51012 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@"

def Usage():
	print "Usage:"
	print "\t",argv[0],"<app_name> <Master board ip> <Slave ips(Min: 1 Max:5)>"
	print "\n\tapp_name can be one of:"
	for app_name in apps:
		print "\t\t\t",app_name
	exit(1)

def Login(child):
        ret=child.expect(["[pP]assword","[yY]es/[nN]o","[yY]/[nN]","[cC]onnection",\
                                                "[Nn]o [rR]oute",TIMEOUT,EOF])
        if ret==0:
                child.sendline(passwd)
        else:
                print "Connection Failed"
                stdout.flush()
                exit(1)

        ret=child.expect(["root@*","[pP]ermission","[wW]rong","[iI]nvalid",TIMEOUT,EOF])
        if ret!=0:
                print "[",ret,"]","Invalid Password or Timed Out"
                stdout.flush()
                exit(1)

def open_cli(child):
        child.sendline("sav_cmd")
        ret=child.expect(["Savari>>",TIMEOUT,EOF])
        if ret != 0:
                print "Failed to Enter into CLI"
                exit(1)

def config_master(master,slaves):
        open_cli(master)
        master.sendline("config rsu-set master enable")
        master.expect("Savari>>")

        master.sendline("config rsu-set commit")
        master.expect("Savari>>")

        while True:
                master.sendline("show rsu-set all")
                ret=master.expect(["[sS]nmp.*[ ]*=[ ]*[0-9].*[0-9]",TIMEOUT,EOF],4)
                if ret == 0:
                        old_slave_ip = master.match.group().split("=")[1].split("\n")[0]
                        master.sendline("config rsu-set delete "+old_slave_ip)
                        master.expect("Savari>>")

                        master.sendline("config rsu-set commit")
                        master.expect("Savari>>")
                        continue
                elif ret == 1:
                        break
                else:
                        print "EOF reached"
                        exit(1)

        for i in slaves:
                master.sendline("config rsu-set add "+i)
                master.expect("Savari>>")

        master.sendline("config rsu-set commit")
        master.expect("Savari>>")

        master.sendline("show rsu-set all")
        master.expect("Savari>>")

def config_slaves(slave_set):
	for slave in slave_set:
			open_cli(slave)
			slave.sendline("config rsu-set master disable")
			slave.expect("Savari>>")
			slave.sendline("config rsu-set commit")
			slave.expect("Savari>>")

#*******************************START**************************************#

try:
	if ( len(argv) > 8 ) or ( len(argv) < 4 ):
		Usage()

	app		= 	argv[1]

	if not app in apps:
		print "Invalid app",app
		Usage()

	master_ip	=	argv[2]
	no_of_slaves	=	len(argv)-3

	slave_ips	= 	[]
	for i in range(no_of_slaves):
		slave_ips.append(argv[i+3])

        try:
                master	=	spawn(sshcmd+master_ip)
        except:
                print "ssh failed",exc_info()
		stdout.flush()
                exit(1)

	master.logfile_read	=	stdout
        master.timeout		=	Timeout

	slave_set		= 	[]

	j=0
	for i in slave_ips:
		try:
			slave_set.append(spawn(sshcmd+i))
			slave_set[j].logfile_read	= stdout
			slave_set[j].timeout		= Timeout
			j				+= 1
		except:
			print "ssh failed for the board",i
			print "Exception:",exc_info()
			exit(1)

	Login(master)
	
	i=0
	while i<j:
		Login(slave_set[i])
		i += 1

	config_master(master,slave_ips)
	

	config_slaves(slave_set)


	if app=="store-repeat":
		from store_and_repeat import *
		while True:
			config_store_and_repeat(master,app)	
			validate_store_and_repeat(master,slave_set,app)
			print "Done\n"
			sleep(5)

	elif app == "bsmforwd":
		from bsmforwd import *
		while True:
			config_bsmforwd(master,app)
			validate_bsmforwd(master,slave_set,app)
			print "Done\n"
			sleep(5)
	elif app == "wsmpforwd":
		from wsmpforwd import *
		while True:
			config_wsmpforwd(master,app)
			validate_wsmpforwd(master,slave_set,app)
			print "Done\n"
			sleep(5)
	elif app == "immediate-forward":
		from immediate_forward import *
		while True:
			config_immediate_forward(master,app)
			validate_immediate_forward(master,slave_set,app)
			print "Done\n"
			sleep(5)
	elif app == "gpsoutput":
		from gpsoutput import *
		while True:
			config_gpsoutput(master,app)
			validate_gpsoutput(master,slave_set,app)
			print "Done\n"
			sleep(5)
	elif app == "radio":
		from radio import *
		while True:
			config_radio(master,app)
			validate_radio(master,slave_set,app)
			print "Done\n"
			sleep(5)
	elif app == "ipv6-provider":
		from ipv6_provider import *
		while True:
			config_ipv6_provider(master,app)
			validate_ipv6_provider(master,slave_set,app)
			print "Done\n"
			sleep(5)
	elif app == "tcd":
		from tcd import *
		while True:
			config_tcd(master,app)
			validate_tcd(master,slave_set,app)
			print "Done\n"
			sleep(5)
	elif app == "dsrc-message-forward":
		from dsrc_message_forward import *
		while True:
			config_dsrc_message_forward(master,slave_set,app)
			validate_dsrc_message_forward(master,slave_set,app)
			print "Done\n"
			sleep(5)

except KeyboardInterrupt:
	pass
except SystemExit:
	pass
except:
	print "Global Exception",exc_info()
	exit(1)
