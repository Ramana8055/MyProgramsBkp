#!/bin/bash
read -p "Enter a Number b/w 1 and 9: " num
for (( i=1 ; i<= num ; i++ ))
do
    for (( j=1 ; j<=i ; j++ ))
    do
        echo -n $j
    done
    echo
done
