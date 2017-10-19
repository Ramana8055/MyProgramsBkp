#!/usr/bin/python -B
import sys
import os
from lxml import etree
#*************************Program to generate denm xml file*********************************

#Author: Ramana Reddy


if len(sys.argv)!=4:
	print "Usage:"
	print "\t",sys.argv[0],"<Output xml file name> <AreaType> <Type>"
	print "\n\tType can be any of (mini,maxi,random,abovemax,belowmin,unavailable)\n"
	print "\n\tAreaType can be one of (circular,rectangular,ellipsoidal)\n"
	sys.exit(1)

output_xml = open(sys.argv[1],'w')
AreaType = sys.argv[2]
Option = sys.argv[3]

if AreaType.lower() != "circular" and AreaType.lower() != "rectangular" and  AreaType.lower() != "ellipsoidal":
	print "\n\tAreaType can be one of (circular,rectangular,ellipsoidal)\n"
	exit(1)


if (Option != "mini" and Option != "maxi" and Option != "unavailable" and Option != "random"
						and  Option != "belowmin" and Option != "abovemax"):
	print "\n\tType can be one of (mini,maxi,random,abovemax,belowmin,unavailable)\n"
	sys.exit(1)

from base import *

def get_sub_tags(local_child,local_sub_tags):
	for subtag in local_sub_tags:
		for subfield in subtag:
			subchild=etree.SubElement(local_child,subfield)
                        if subtag[subfield]["dtype"]=="structure":
				if subtag[subfield]["repeat"] == "yes":
					for _ in range(0,int(subtag[subfield]["repeatcount"])):
						get_sub_tags(subchild,subtag[subfield]["taglist"])
				else:
					get_sub_tags(subchild,subtag[subfield]["taglist"])
			elif subtag[subfield]["dtype"]=="string":
                                subchild.text=subtag[subfield]["String"]()
			elif subtag[subfield]["dtype"]=="choice":
                                subchild.text=subtag[subfield]["first"]
			elif subtag[subfield]["dtype"] == "AreaType":
				if AreaType.lower()=="circular":
					subchild.text="Circular"
					local_child.append(subchild)
					newchild=etree.SubElement(local_child,"circularArea")
					get_sub_tags(newchild,subtag[subfield]["Circular"])
					return
				elif AreaType.lower()=="rectangular":
					subchild.text="Rectangular"
					local_child.append(subchild)
					newchild=etree.SubElement(local_child,"rectangularArea")
					get_sub_tags(newchild,subtag[subfield]["Rectangular"])
					return
				elif AreaType.lower()=="ellipsoidal":
					subchild.text="Ellipsoidal"
					local_child.append(subchild)
					newchild=etree.SubElement(local_child,"ellipsoidalArea")
					get_sub_tags(newchild,subtag[subfield]["Ellipsoidal"])
					return
			elif subtag[subfield]["dtype"]=="value":
				if Option == "mini":
					subchild.text=subtag[subfield]["mini"]
				elif Option == "maxi":
					subchild.text=subtag[subfield]["maxi"]
				elif Option == "unavailable":
					subchild.text=subtag[subfield]["unavailable"]
				elif Option == "random":
					subchild.text=subtag[subfield]["random"](subtag[subfield]["mini"],subtag[subfield]["maxi"])
				elif Option == "belowmin":
					subchild.text=subtag[subfield]["belowmin"](-1000000000000,subtag[subfield]["mini"])
				elif Option == "abovemax":
					subchild.text=subtag[subfield]["abovemax"](subtag[subfield]["maxi"],1000000000000)
			local_child.append(subchild)


root=etree.Element("denm")

for tag in xml_tags:
	for field in tag:
		child=etree.SubElement(root,field)
		if tag[field]["dtype"]=="structure":
			if tag[field]["repeat"] == "yes":
				for _ in range(0,int(tag[field]["repeatcount"])):
					get_sub_tags(child,tag[field]["taglist"])
			else:
				get_sub_tags(child,tag[field]["taglist"])

		elif tag[field]["dtype"]=="choice":
			child.text=tag[field]["first"]
		elif tag[field]["dtype"]=="string":
			child.text=tag[field]["String"]()
		elif tag[field]["dtype"]=="value":
			if Option == "mini":
				child.text=tag[field]["mini"]
			elif Option == "maxi":
				child.text = tag[field]["maxi"]
			elif Option == "unavailable":
				child.text = tag[field]["unavailable"]
			elif Option == "random":
				child.text = tag[field]["random"](tag[field]["mini"],tag[field]["maxi"])
			elif Option == "belowmin":
				child.text = tag[field]["belowmin"](-1000000000000,tag[field]["mini"])
			elif Option == "abovemax":
				child.text = tag[field]["abovemax"](tag[field]["maxi"],1000000000000)
		root.append(child)		
output_xml.write(etree.tostring(root,pretty_print=True))
#sys.stdout.write(etree.tostring(root,pretty_print=True))
