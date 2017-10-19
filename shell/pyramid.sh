#!/bin/bash
read -p "Enter a number: " num
for (( i=1; i<=num ; i++ ))
do
	for (( k=num-i ; k>0 ; k-- ))
	do
		echo -n " "
	done

	for (( j=1 ; j<=i ; j++ ))
	do
		echo -n "$i "
	done
	echo
done
	
