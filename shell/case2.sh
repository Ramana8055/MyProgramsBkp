#!/bin/bash
echo enter any character
read char
case $char in
	[a-z]) echo Lower case letter
			;;
	[A-Z]) echo Upper case letter
			;;
	[0-9]) echo Number
			;;
	?) echo Special character
			;;
	*) echo You entered more than one character 
			;;
esac
