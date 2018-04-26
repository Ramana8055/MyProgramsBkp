#!/bin/bash

read -p "Enter a number: " num

for (( i=1 ; i<=num ; i++ ))
do
    for (( j=1 ; j<=i ; j++ ))
    do
        if [ $j -eq $i ]
        then
            echo -n '|_'
        elif [ $j -ne 1 ]
        then
            echo -n '|'
        else
            echo -n '|'
        fi
    done
    echo 
done
