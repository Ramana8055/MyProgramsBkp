#!/bin/bash
echo "until"
i=1;
until [ $i -gt 10 ]
do
    echo $i
    i=`expr $i + 1`
done
echo "while"
j=1;

while [ $j -gt 10 ]
do
    echo $j
    j=`expr $j + 1`
done
