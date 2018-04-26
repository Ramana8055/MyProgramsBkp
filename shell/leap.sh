#!/bin/bash
if [ $# -eq 0 ]
then
    year=`date +%Y`
    if [ $(( year % 4 )) -eq 0 ]
    then
        if [ $(( year % 100 )) -eq 0 ]
        then
            echo "$year is not a leap year"
        else
            echo "$year is a leap year"
        fi
    else
        echo "$year is not a leap year"
    fi
else
    year=$1
    if [ $(( year % 4 )) -eq 0 ]
        then
                if [ $(( year % 100 )) -eq 0 ]
                then
                        echo "$year is not a leap year"
                else
                        echo "$year is a leap year"
                fi
        else
                echo "$year is not a leap year"
        fi
fi


