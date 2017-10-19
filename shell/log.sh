#!/bin/bash
pwd

who | grep ramana | grep pts

if [ $? -eq 0 ]
then
	echo "hello" | write ramana
else
	echo "hello" | mail ramana
fi
