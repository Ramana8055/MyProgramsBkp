#Program to Merge two csv files column by column into another csv file
#i.e, first column of first file in first column and first column of
#second file in second column and so on..............................

#!/bin/bash
if [ $# -ne 2 ]; then
    echo "Parse two csv files at the command line"
    exit
fi
file1="$1"
file2="$2"
if [ ! -f "$file1" ] ; then
    echo "$file1 doesn't exist"
    exit
fi
if [ ! -f "$file2" ] ; then
    echo "$file2 doesn't exist"
    exit
fi

x=1
max=`awk -F, 'NR==1{print NF}' $file1`
while [ $x -le $max ]
do
    if [ $x -eq 1 ] ; then
        paste -d, <(awk -F, '{print $'$x'}' $file1) <(awk -F, '{print $'$x'}' $file2) > prefinal.csv
    elif [ $x -eq $max ] ; then
        paste -d, <(awk '{print $0}' prefinal.csv) <(awk -F, '{print $'$x'}' $file1) <(awk -F, '{print $'$x'}' $file2) > final.csv
    else
        paste -d, <(awk '{print $0}' prefinal.csv) <(awk -F, '{print $'$x'}' $file1) <(awk -F, '{print $'$x'}' $file2) > final.csv
        cp final.csv prefinal.csv
    fi
    x=`expr $x + 1`
done
rm prefinal.csv
