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
		echo -n ". "
	done
	echo
done
for (( i=num ; i>0 ; i-- ))
do
	for (( k=0 ; k<num-i ; k++ ))
	do
		echo -n " "
	done
	for (( j=1 ; j<=i ; j++ ))
	do
		echo -n ". "
	done
	echo
done
	
