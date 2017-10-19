#!/usr/bin/python
from sys import argv
#fd=file(argv[1],'r')
#fd2=file(argv[2],"w")
#fd2.write(fd.read())

open(argv[2],'w').write(open(argv[1],'r').read())
