#!/bin/bash
echo Enter a no b/w 1 to 3
read num

case $num in
    1) echo you entered 1
        ;;
    2) echo you entered 2
        ;;
    3) echo you entered 3
        ;;
    *) echo I said 1 to 3!!!
        ;;
esac
