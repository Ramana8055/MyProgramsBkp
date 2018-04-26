#!/usr/bin/python

"""Program to print number of occurances of an alphabet"""

import sys

num_occurances={}

if len(sys.argv) != 2:
    print sys.argv[0], '"<string>"'
    sys.exit(1)

for char in sys.argv[1]:
    if char in num_occurances:
        num_occurances[char] += 1
    else:
        num_occurances[char] = 1

for i in num_occurances:
    if i == " ":
        continue
    print "%s : %d" % (i, num_occurances[i])

