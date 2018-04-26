#!/bin/bash
echo "Enter S.P"
read sp
echo "Enter C.P"
read cp

echo "S.P=$sp and C.P=$cp"

if [ $sp -gt $cp ]
then 
	echo "Profit"
	echo `expr $sp - $cp`
elif [ $sp -lt $cp ]
then
	echo "Loss"
	echo ` expr $cp - $sp`
else
	echo "No loss No profit"
fi
