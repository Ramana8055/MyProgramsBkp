
read -p "enter a string in double quotes :  " x


grep -o " " <<< "$x" | wc -l
