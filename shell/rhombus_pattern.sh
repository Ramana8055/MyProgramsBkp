#!/bin/bash
MAX_NO=0

echo -n "Enter a no. b/w 5 to 9 : "
read MAX_NO

if ! [ $MAX_NO -ge 5 -a $MAX_NO -le 9 ];
then
	echo "Hey enter no b/w 5 and 9"
	exit 1
fi
clear
for (( i=1; i<=MAX_NO; i++))
do
	for (( s=MAX_NO; s>=i; s--))
	do
		echo -n " "
	done
	for (( j=1; j<=i; j++)) 
	do 
		echo -n " ."
	done
	echo ""
done


for (( i=MAX_NO; i>=1; i--)) 
do
	for(( s=i; s<=MAX_NO; s++))
	do
		echo -n " "
	done

	for (( j=1; j<=i; j++))
	do
		echo -n " ."
	done
	echo ""
done
echo -e "\n\n\t\t\t That's it"
