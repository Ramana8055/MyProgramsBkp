#!/usr/bin/python -B
from pexpect import *
from sys import stdout,exit

#child = spawn('ssh localhost')
#child.logfile=stdout
#child.setecho(False)
#child.expect('(?i)password')
#child.sendline("rams@cdac20")
#child.interact()

#similar thing is done by
run('ssh localhost', events={'(?i)password': "rams@cdac20\n"},logfile=stdout)
