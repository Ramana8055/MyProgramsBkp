#!/usr/bin/python
## ip, username, password, command in csv file

import sys
import paramiko
import csv
if (len(sys.argv) != 2):
	print "Parse a csv file with ip "+\
		"username, password and command in each row"
	sys.exit(1)
clist = []
f = open(sys.argv[1], "rt")
reader = csv.reader(f)
for row in reader:
	clist.append(row)
f.close()
for row_val in clist:
	ip=row_val[0]
	usr=row_val[1]
	psw=row_val[2]
	command=row_val[3]
	print ip, usr, psw, command
	ssh = paramiko.SSHClient()
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ip, username=usr, password=psw)
	stdin, stdout, stderr= ssh.exec_command(command)
