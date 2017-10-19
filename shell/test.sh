#!/bin/bash
read -p "Enter file 1: " file1
read -p "Enter file 2: " file2

read -p "Enter number of lines to test : " nol

echo
echo "Checking OBE_ID......."
tnol=`awk 'BEGIN{FS=","}NR==FNR{c[$19]++;next};c[$19]>0' $file1 $file2 | wc -l`
if [ $tnol -eq $nol ]
then
        echo "OBE_IDs matched"
else
        echo "OBE_ID Mismatch"
	echo "check the \"error.txt\" file in the current directory"
        awk -F, 'NR==FNR{ c[$19]=$19;print $19;next } NF{ print $19 (( c[$19]==$19)?" ":",mismatch")}' $file1 $file2 > error.txt
        return 1
fi


echo
echo "Checking msgCnt......."
tnol=`awk 'BEGIN{FS=","}NR==FNR{c[$24]++;next};c[$24]>0' $file1 $file2 | wc -l`
if [ $tnol -eq $nol ]
then
        echo "msgCnt Matched"
else
        echo "msgCnt Mismatch"
	echo "check the \"error.txt\" file in the current directory"
        awk -F, 'NR==FNR{ c[$24]=$24;print $24;next } NF{ print $24 (( c[$24]==$24)?" ":",mismatch")}' $file1 $file2 > error.txt
        return 1
fi



echo
echo "Checking TempID......"
tnol=`awk 'BEGIN{FS=","}NR==FNR{c[$25]++;next};c[$25]>0' $file1 $file2 | wc -l`
if [ $tnol -eq $nol ]
then
        echo "TempIDs Matched"
else
        echo "TempID Mismatch"
	echo "check the \"error.txt\" file in the current directory"
        awk -F, 'NR==FNR{ c[$25]=$25;print $25;next } NF{ print $25 (( c[$25]==$25)?" ":",mismatch")}' $file1 $file2 > error.txt
        return 1
fi


echo
echo "Checking Mode........"
tnol=`awk 'BEGIN{FS=","}NR==FNR{c[$4]++;next};c[$4]>0' $file1 $file2 | wc -l`
if [ $tnol -eq $nol ]
then
	echo "Modes Matched"
else
	echo "Mode Mismatch"
	echo "check the \"error.txt\" file in the current directory"
        awk -F, 'NR==FNR{ c[$4]=$4;print $4;next } NF{ print $4 (( c[$4]==$4)?" ":",mismatch")}' $file1 $file2 > error.txt
	return 1
fi



echo
echo "Checking SecMark......"
tnol=`awk 'BEGIN{FS=","}NR==FNR{c[$27]++;next};c[$27]>0' $file1 $file2 | wc -l`
if [ $tnol -eq $nol ]
then
        echo "secMark matching"
else
        echo "secMark Mismatch"
	echo "check the \"error.txt\" file in the current directory"
        awk -F, 'NR==FNR{ c[$27]=$27;print $27;next } NF{ print $27 (( c[$27]==$27)?" ":",mismatch")}' $file1 $file2 > error.txt
        return 1
fi


echo
echo "Checking Latitudes....."
tnol=`awk 'BEGIN{FS=","}NR==FNR{c[$28]++;next};c[$28]>0' $file1 $file2 | wc -l`
if [ $tnol -eq $nol ]
then
        echo "latitudes matching"
else
        echo "latitudes Mismatch"
	echo "check the \"error.txt\" file in the current directory"
        awk -F, 'NR==FNR{ c[$28]=$28;print $28;next } NF{ print $28 (( c[$28]==$28)?" ":",mismatch")}' $file1 $file2 > error.txt
        return 1
fi


echo
echo "Checking Longitudes....."
tnol=`awk 'BEGIN{FS=","}NR==FNR{c[$29]++;next};c[$29]>0' $file1 $file2 | wc -l`
if [ $tnol -eq $nol ]
then
        echo "Longitude matching"
else
        echo "Longitude Mismatch"
	echo "check the \"error.txt\" file in the current directory"
        awk -F, 'NR==FNR{ c[$29]=$29;print $29;next } NF{ print $29 (( c[$29]==$29)?" ":",mismatch")}' $file1 $file2 > error.txt
        return 1
fi


echo
echo "Checking Elevation......"
tnol=`awk 'BEGIN{FS=","}NR==FNR{c[$30]++;next};c[$30]>0' $file1 $file2 | wc -l`
if [ $tnol -eq $nol ]
then
        echo "Elevation matching"
else
        echo "Elevation Mismatch"
	echo "check the \"error.txt\" file in the current directory"
        awk -F, 'NR==FNR{ c[$30]=$30;print $30;next } NF{ print $30 (( c[$30]==$30)?" ":",mismatch")}' $file1 $file2 > error.txt
        return 1
fi

echo "*****Everything is perfect*****"
rm error.txt
