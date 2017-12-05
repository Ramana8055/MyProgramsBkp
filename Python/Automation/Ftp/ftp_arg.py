#!/usr/bin/python -B

#**************************************************************
#Program to download latest file from a FTP directory specified
#**************************************************************
#Tested with vsftp,may be compatibile with others
#**************************************************************
#Author: K Ramana Reddy
#**************************************************************

from sys        import stdout,exit,argv,exc_info
from os         import system
from pexpect    import spawn,EOF,TIMEOUT
from time       import sleep

if len(argv) != 6:
    print "Usage:"
    print "\t",argv[0],"<IP Address> <Username> <Password> <Directory-Path> <image_name>"
    print "\n\t","Use \"\" if there is no password\n"
    exit(1)

ip      = str(argv[1])
usr     = str(argv[2])
pswd    = str(argv[3])
path    = str(argv[4])
img     = str(argv[5])

try:
    try:
        child = spawn("ftp " + ip)
    except:
        print "failed to connect " + exc_info()[0]
        exit(1)

    child.timeout = 1600
    #child.logfile_read = stdout

    x = child.expect(['[nN]ame', EOF, TIMEOUT])
    if x!=0:
        print "No \"Name\" prompt"
        exit(1)

    child.sendline(usr)
    x = child.expect(["[pP]assword", "logged in",
                EOF, TIMEOUT])
    if x == 0:
        child.sendline(pswd)
        y = child.expect(["[lL]ogin [sS]uccess", "User " +usr + " logged in",
                        "[lL]ogin [fF]ailed", EOF, TIMEOUT])
        if y != 0 and y != 1:
            print "Login Failed"
            exit(1)

    elif x != 1:
        print "Authentication Timed Out!!"
        exit(1) 
    child.sendline("cd " + path)
    x = child.expect(["[dD]irectory successfully changed", "CWD command successful",
                                    EOF, TIMEOUT])
    if x != 0 and x != 1:
        print "cd Failed!!!"
        exit(1)

    child.sendline("ls -lt")

    x = child.expect([img, "[tT]ransfer [cC]omplete", "[dD]irectory", TIMEOUT, EOF])
    if x == 0:
        image = child.match.group().split("\n")[0]
        print image
    elif x == 1 or x == 2:
        print "There are no images in the directory"
        exit(1)
    else:
        print "Connection Timedout or terminated"
        exit(1)

    child.sendline("binary")
    child.expect("ftp>")

    child.sendline("get " + image)
    x = child.expect(["[tT]ransfer [cC]omplete",
                EOF, TIMEOUT])
    if x != 0:
        print "Copy Failed"
        exit(1)

    system("sync")
    child.close()

except KeyboardInterrupt:
    print "",
    exit(0)
except SystemExit:
    print "",
    exit(0)
except:
    print "Global Exception", exc_info()[0]
    exit(1)
