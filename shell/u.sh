#!/bin/bash

read -p "Enter PreRefFile1: " file1
read -p "Enter File2: " file2

nol=( `cat $file1 | wc -l` )

x=1
while [ $x -le $nol ]
do
	awk -v var="$x" -F, 'NR==var{a[$4$19$24$25]=1;next};($4$19$24$25 in a)' $file1 $file2 >> new_matched.csv
	x=( `expr $x + 1` )
done

tnol=( `cat new_matched.csv | wc -l` )

if [ $tnol -ne $nol ]
then
	echo "No of matches are $tnol"
fi

tnol=( `awk -F, 'NR==FNR{c[$27]++;next};c[$27]>0' $file1 new_matched.csv | wc -l` )
if [ $tnol -eq $nol ]
then
        echo "SecMark Matched" 
else
        awk -F, 'NR==FNR{c[$27]=$27;next} NF{print $27 ((c[$27]==$27)?" ":",mismatch")}' $file1 $file2 | cat -n | grep mismatch
fi

tnol=( `awk -F, 'NR==FNR{c[$28]++;next};c[$28]>0' $file1 new_matched.csv | wc -l` )
if [ $tnol -eq $nol ]
then
        echo "Latitudes Matched" 
else
        awk -F, 'NR==FNR{c[$28]=$28;next} NF{print $28 ((c[$28]==$28)?" ":",mismatch")}' $file1 $file2 | cat -n | grep mismatch
fi

echo "Do you want to remove output file[y/n]"
read input
if [ $input == y ]
then 
	rm new_matched.csv
fi


