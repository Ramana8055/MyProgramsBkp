#!/bin/bash
read -p "Enter two files" file1 file2

cmp $file1 $file2 > result
if [ $? -eq 0 ]
then
	echo "Both are Similar files"
	echo "deleting second file"
	rm $file2
else
	cat result
fi
