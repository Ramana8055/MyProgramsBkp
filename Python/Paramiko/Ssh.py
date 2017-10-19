#!/usr/bin/python
import sys
import paramiko
if(len(sys.argv) < 5 or len(sys.argv) > 6):
	print "Usage:i "+sys.argv[0]+" <ip> <username> <Password> <Command> <port(Optional)>",
	sys.exit(1)
ip=sys.argv[1]
usr=sys.argv[2]
Psw=sys.argv[3]
Cmd=sys.argv[4]
try:
	if(len(sys.argv)==6):
		Port=int(sys.argv[5])
		if(Port<1 or Port>65535):
			print "Use a port in the range 1-65535",
			sys.exit(1)
	else:
		Port=22
	ssh = paramiko.SSHClient()
	#ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ip,port=Port, username=usr,password=Psw)
	stdin, stdout, stderr= ssh.exec_command(Cmd)
	print stdout.read(),stderr.read(),
except KeyboardInterrupt:
	print ""
