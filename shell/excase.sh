#!/bin/bash
echo Enter any character
read char
case $char in
    [[:lower:]]) echo Lower case letter
            ;;
    [[:upper:]]) echo Upper case letter
            ;;
    [[:digit:]]) echo Number
            ;;
    ?) echo Special char
            ;;
    *) echo You entered more than one character 
            ;;
esac
