#!/bin/bash
read -p "Enter file1 : " file1
read -p "Enter file2 : " file2

read -p "Enter number of lines : " nol

flag=0

tol=`awk -F, 'NR==FNR{c[$19$24$25]++;next};c[$19$24$25]>0' $file1 $file2 | wc -l`

if [ $tol -eq $nol ]
then
	echo -n	
else
	awk -F, 'NR==FNR{c[$19$24$25]=$19$24$25;next} NF{print $19$24$25 ((c[$19$24$25]==$19$24$25)?" ":",mismatch")}' $file1 $file2 | cat -n | grep mismatch 
	flag=1
fi

if [ $flag -eq 0 ]
then
	echo "Identity Matched"
else
	echo "Identity Mismatch"
fi

tol=`awk -F, 'NR==FNR{c[$4]++;next};c[$4]>0' $file1 $file2 | wc -l`
if [ $tol -eq $nol ]
then 
	echo -n
else
	echo "Mode mismatch"
	awk -F, 'NR==FNR{c[$4]=$4;next} NF{print $4 ((c[$4]==$4)?" ":",mismatch")}' $file1 $file2 | cat -n | grep mismatch
fi


tol=`awk -F, 'NR==FNR{c[$27]++;next};c[$27]>0' $file1 $file2 | wc -l`
if [ $tol -eq $nol ]
then
        echo -n
else
        echo "SecMark mismatch"
        awk -F, 'NR==FNR{c[$27]=$27;next} NF{print $27 ((c[$27]==$27)?" ":",mismatch")}' $file1 $file2 | cat -n | grep mismatch
fi


tol=`awk -F, 'NR==FNR{c[$28]++;next};c[$28]>0' $file1 $file2 | wc -l`
if [ $tol -eq $nol ]
then
        echo -n
else
        echo "Latitude mismatch"
        awk -F, 'NR==FNR{c[$28]=$28;next} NF{print $28 ((c[$28]==$28)?" ":",mismatch")}' $file1 $file2 | cat -n | grep mismatch
fi

tol=`awk -F, 'NR==FNR{c[$29]++;next};c[$29]>0' $file1 $file2 | wc -l`
if [ $tol -eq $nol ]
then
        echo -n
else
        echo "Longitude mismatch"
        awk -F, 'NR==FNR{c[$29]=$29;next} NF{print $29 ((c[$29]==$29)?" ":",mismatch")}' $file1 $file2 | cat -n | grep mismatch
fi

tol=`awk -F, 'NR==FNR{c[$30]++;next};c[$30]>0' $file1 $file2 | wc -l`
if [ $tol -eq $nol ]
then
        echo -n
else
        echo "Elevation mismatch"
        awk -F, 'NR==FNR{c[$30]=$30;next} NF{print $30 ((c[$30]==$30)?" ":",mismatch")}' $file1 $file2 | cat -n | grep mismatch
fi
