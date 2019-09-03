#!/bin/bash
while getopts ab:cd choice
do
	case $choice in
			a) echo "You entered a";;
			b) echo "You entered b with arg $OPTARG" ;;
			c) echo "You entered c";;
			d) echo "You entered d";;
			?) echo "You entered wrong choice";;
	esac
done
