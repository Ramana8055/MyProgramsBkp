#!/bin/bash

while getopts "b:m:" opt; do

	case $opt in
			a) echo "m is invoked with $OPTARG";;
			b) echo "b is invoked with $OPTARG";;
			*) echo "Invalid switch"
	esac
done

echo "$@"
