#!/bin/bash
read -p "Eneter 1 for UID and 2 for LOGNAME" choice
if [ $choice -eq 1 ]
then
	read -p "Enter UID:  " uid
	logname="`cat /etc/passwd | grep $uid | cut -f1 -d:`"
else
	read -p "Enter Logname:  " logname
fi
not="`ps -au$logname | grep -c bash`"
echo  "The number of terminals opened by $logname are $not"



