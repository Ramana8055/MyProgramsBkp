#!/bin/bash

read -p "Enter PreRefFile1: " file1
read -p "Enter File2: " file2

file3=logresult.csv
file4=result.txt
nol=( `cat $file1 | wc -l` )

x=1
while [ $x -le $nol ]
do
	awk -v var="$x" -F, 'NR==var{a[$4$19$24$25]=1;next};($4$19$24$25 in a)' $file1 $file2 >> $file3
	x=( `expr $x + 1` )
done

tnol=( `cat $file3 | wc -l` )

if [ $tnol -ne $nol ]
then
	echo "No of matches are $tnol"
fi

tnol=( `awk -F, 'NR==FNR{c[$27]++;next};c[$27]>0' $file1 $file3 | wc -l` )
if [ $tnol -eq $nol ]
then
        echo "SecMark Matched" 
else
	echo -e "SecMark:\n" >> $file4
	echo "  Line	SecMark\n" >> $file4
        awk -F, 'NR==FNR{c[$27]=$27;next} NF{print $27 ((c[$27]==$27)?" ":",mismatch")}' $file1 $file3 | cat -n | grep mismatch >> $file4
	echo >> $file4
fi

tnol=( `awk -F, 'NR==FNR{c[$28]++;next};c[$28]>0' $file1 $file3 | wc -l` )
if [ $tnol -eq $nol ]
then
        echo "Latitudes Matched" 
else
	echo -e "Latitudes:\n" >> $file4
	echo "  Line	Latitude" >> $file4
        awk -F, 'NR==FNR{c[$28]=$28;next} NF{print $28 ((c[$28]==$28)?" ":",mismatch")}' $file1 $file3 | cat -n | grep mismatch >> $file4
	echo >> $file4
fi

tnol=( `awk -F, 'NR==FNR{c[$29]++;next};c[$29]>0' $file1 $file3 | wc -l` )
if [ $tnol -eq $nol ]
then
        echo "Longitudes Matched" 
else
	echo -e "Longitudes:\n" >> $file4
	echo "  Line	Longitude" >> $file4
        awk -F, 'NR==FNR{c[$29]=$29;next} NF{print $29 ((c[$29]==$29)?" ":",mismatch")}' $file1 $file3 | cat -n | grep mismatch >> $file4
	echo >> $file4
fi

tnol=( `awk -F, 'NR==FNR{c[$30]++;next};c[$30]>0' $file1 $file3 | wc -l` )
if [ $tnol -eq $nol ]
then
        echo "Elevation Matched" 
else
	echo -e "Longitudes:\n" >> $file4
	echo "  Line	Elevation" >> $file4
        awk -F, 'NR==FNR{c[$30]=$30;next} NF{print $30 ((c[$30]==$30)?" ":",mismatch")}' $file1 $file3 | cat -n | grep mismatch >> $file4
	echo >> $file4
fi

echo "Do you want to remove output file[y/n]"
read input
if [ $input == y ]
then 
	rm $file3 $file4
fi


