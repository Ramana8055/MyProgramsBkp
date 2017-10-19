#!/usr/bin/python3 -B
from sys import stdout,exc_info,exit,argv
from csv import reader
from can_base import *
def Usage():
	print('Usage:')
	print('\t',argv[0],'<csv file with CAN standard messages(600-605)>')
	exit(1)
try:
	if len(argv) != 2:
		Usage()
	try:
		with open(argv[1], 'r') as csvfile:
			Csvreader=reader(csvfile, delimiter=',')
			i = 0
			for row in Csvreader:
				i += 1
				if i == 1:
					continue

				print("CAN Message set:", i-1)

				m600 = []
				for j in range(0, 11):
					if row[j] == "":
						row[j] = 0
					m600.append(row[j])
				print("\t600",message_600(m600))
			
				m601 = []
				for j in range(11, 25):
					if row[j] == "":
						row[j] = 0
					m601.append(row[j])
				print("\t601",message_601(m601))
				
	except IOError:
		print('Failed to open', csvfile.name)
		exit(1)
except KeyboardInterrupt:
	exit(0)
except SystemExit:
	pass
except:
	print("Global exception", exc_info())
	exit(1)
