#!/bin/bash
case $1 in
	cat | dog) echo cat
		;;
	d) echo dog
		;;
	*) echo animal!!
		;;
esac
