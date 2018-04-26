#!/bin/bash
read -p "Enter a number : " num
for (( i=1 ; i<=num ; i++ ))
do
        for (( j=1 ; j<=i ; j++ ))
        do
                echo -n \*
        done
        echo
done
for (( i=num ; i>0 ; i-- ))
do
    for (( j=1 ; j<=i ; j++ ))
    do
        echo -n \*
    done
    echo
done
