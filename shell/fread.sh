#!/bin/bash
echo "Enter a file name"
read fname
terminal=`tty`
exec < $fname

while read line
do 
   echo $line
done

exec < $terminal
