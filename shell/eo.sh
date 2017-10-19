#!/bin/bash
echo "Enter any number"
read i

if [ $((i%2)) -eq 0 ]
then
	echo "Even  Number"
else
	echo "Odd Number"
fi
echo $#
