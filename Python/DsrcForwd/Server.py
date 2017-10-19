#!/usr/bin/python
import sys
import socket
def Usage():
	print "Usage:"
	print "\t"+sys.argv[0]+" "+"<port> <protocol> <infusion>"
	print "\t\t Ports Range: 1023-65535"
	print "\t\t Protocols: tcp (or) udp"
	print "\t\t Infusion:  0 or 1"
	sys.exit(1)

if(len(sys.argv) != 4):
	Usage()

port = int(sys.argv[1])
if(port < 1024 or port > 65535):
	print "Invalid Port",sys.argv[1]
	Usage()

proto = sys.argv[2]
if(proto.lower() != "tcp" and proto.lower() != "udp"):
	print "Invalid Protocol",sys.argv[2]
	Usage()

server_addr = ("", port)

inf = int(sys.argv[3])

if(inf != 0 and inf !=1):
	print "Invalid infusion value",sys.argv[3]
	Usage()

try:
	if (proto.lower() == "tcp"):
		try:
			soc=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		except socket.error, err:
			print "Failed to create socket: ["+str(err[0])+"] "+err[1]
			sys.exit(1)
		try:
			soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
		except socket.error, err:
			print "Setsockopt Failed: ["+str(sys.err[0])+"] "+err[1]
			sys.exit(1)
		try:
			soc.bind(server_addr)
		except socket.error, err:
			print "Failed to bind: ["+str(err[0])+"] "+err[1]
			sys.exit(1)
		soc.listen(1)
		try:  #Keep this in while loop later 
			soc.accept()
		except socket.error, err:
			print "Failed to accept ["+str(err[0])+"] "+err[1]
			sys.exit(1)
		while True:
			try:
				ret=soc.recv(1400)
				if ret == "":
					print "Receive Failed"	
					sys.exit(1)
				siz = len(ret)
				for i in range(0, siz-1):
					print "%02X " % ord(ret[i]),
				print ""
			except socket.error, err:
				print "Recv Failed: ["+str(err[0])+"] "+err[1]
				sys.exit(1)
	else:
		try:
			soc=socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
		except socket.error, err:
			print "Failed to create socket: ["+str(err[0])+"] "+err[1]
			sys.exit(1)
		try:
			soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
		except socket.error, err:
			print "Setsockopt Failed: ["+str(sys.err[0])+"] "+err[1]
			sys.exit(1)
		try:
			soc.bind(server_addr)
		except socket.error, err:
			print "Failed to bind: ["+str(err[0])+"] "+err[1]
			sys.exit(1)
		while True:
			try:
				ret,_ = soc.recvfrom(1400)
				if ret == "":
					print "Receive Failed"
					sys.exit(1)
				siz = len(ret)
				for i in range(0, siz-1):
					print "%02X " % ord(ret[i]),
				print ""
			except socket.error, err:
				print "RecvFrom Failed: ["+str(err[0])+"] "+err[1]
				sys.exit(1)
except KeyboardInterrupt:
	print ""
except SystemExit:
	pass
except:
	print "Global Exception",sys.exc_info()
	sys.exit(1)
