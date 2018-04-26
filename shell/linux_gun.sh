#!/bin/bash

read -p "Enter a number: " num

for (( i=1 ; i<=num ; i++ ))
do
    for (( j=1 ; j<=i ; j++ ))
    do
        if [ $j -eq $num ]
        then
            echo -n "______>> Powered Server."
        elif [ $j -eq $i ]
        then
            echo -n "|Linux______"
        else
            echo -n "|Linux"
        fi
    done
    echo
done

for (( i=num-1 ; i>0 ; i-- ))
do
    for (( j=1 ; j<=i ; j++ ))
    do
        if [ $j -eq $i ]
        then
            echo -n "|Linux~~~~~~"
        else
            echo -n "|Linux"
        fi
    done
    echo
done
