#!/usr/bin/python3 -B
from sys import stdout,exc_info,exit,argv
from csv import reader
def twos_comp(val, bits):
    if (val & (1 << (bits - 1))) != 0: 
        val = val - (1 << bits)
    return val

def message_601(m601):
	angle=int(float(m601[0])/0.031250)
	if angle<0:
		temp = twos_comp(abs(angle),16)
	else:
		temp = angle

	b1 = temp>>8
	b2 = temp & 0x00ff
	Temperature = int((float(m601[1])+40)/0.5)

	if Temperature<0:
		b3 = twos_comp(abs(Temperature),8)
	else:
		b3 = Temperature

	Speed = int(float(m601[2])/0.01)

	b4 = Speed>>8
	b5 = Speed & 0x00ff

	Acceleration = int((float(m601[3])+9.9)/0.0194)

	if Acceleration<0:
		temp = twos_comp(abs(Acceleration),10)
	else:
		temp = Acceleration

	Panic     = int(m601[4])
	Charge    = int(m601[5])
	HeadLight = int(m601[6])
	Wiper     = int(m601[7])

	temp = (temp<<1) | Panic
	temp = (temp<<1) | Charge
	temp = (temp<<1) | HeadLight
	temp = (temp<<3) | Wiper 

	b6 = temp >> 8
	b7 = temp & 0x00ff

	IDS = ( int(m601[8])  ) <<7
	AB  = ( int(m601[9])  ) <<6 
	HBS = ( int(m601[10]) ) <<5
	WSS = ( int(m601[11]) ) <<4

	WiperStatus = (int(m601[12])<<1)

	b8 = IDS | AB | HBS | WSS | WiperStatus
		
	return " ".join(map(lambda x: "%02X" % x, [b1,b2,b3,b4,b5,b6,b7,b8]))

def message_600(m600):
	b1=0
	for i in range(0,4):               #Remove for loop and validate blank data
		b1=(b1<<1)|int(m600[i])
	b1=(b1<<4)|int(m600[4])

	b2=int(m600[5])

	b3=(int(m600[6])<<7)

	b4=int(m600[8])

	temp=int(float(m600[9])/0.01)

	b5=temp>>8

	b6=temp & 0x00ff

	yaw=int(float(m600[10])*100)

	if yaw<0:	
		temp=twos_comp(abs(yaw),16)
	else:
		temp=yaw

	b7= temp>>8
	b8=temp & 0x00ff

	return " ".join(map(lambda x: "%02X" % x,[b1,b2,b3,b4,b5,b6,b7,b8]))
def Usage():
	print('Usage:')
	print('\t',argv[0],'<csv file> in CAN standard messages(600-605)')
	exit(1)
try:
	if len(argv)!=2:
		Usage()
	try:
		with open(argv[1],'r') as csvfile:
			Csvreader=reader(csvfile,delimiter=',')
			i=0
			for row in Csvreader:
				i+=1
				if i==1:
					continue
				m600=[]
				for j in range(0,11):
					if row[j] == "":
						row[j] = 0
					m600.append(row[j])
				print(message_600(m600))
			
				m601=[]
				for j in range(11,25):
					if row[j] == "":
						row[j] = 0
					m601.append(row[j])
				print(message_601(m601))
				
	except IOError:
		print('Failed to open',csvfile.name)
		exit(1)
#except NameError:
#	print("Invalid file")
except KeyboardInterrupt:
	exit(0)
except SystemExit:
	pass
except:
	print("Global exception",exc_info())
	exit(1)
