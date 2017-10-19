#!/usr/bin/python
import sys
import paramiko
import time
if(len(sys.argv) < 5 or len(sys.argv) > 6):
	print "Usage: "+sys.argv[0]+" <ip> <username> <Password> <Command> <port(Optional)>",
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
	ssh.load_system_host_keys()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(ip,port=Port, username=usr,password=Psw)
	transport = ssh.get_transport()
	session = transport.open_session()
	session.setblocking(0) # Set to non-blocking mode
	session.get_pty()
	session.invoke_shell()

	# Send command
	session.send(Cmd+"\n")
	# Loop for 10 seconds
	start = time.time()    
	while time.time() - start < 10:
	  if session.recv_ready():
	    data = session.recv(512)
	    sys.stdout.write(data)
	    sys.stdout.flush() # Flushing is important!

	  time.sleep(0.001) # Yield CPU so we don't take up 100% usage...

	session.send('\x03')
	session.close()
	print
except KeyboardInterrupt:
	print ""
