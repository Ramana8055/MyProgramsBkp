#!/usr/bin/expect --

spawn scp -P 51012 "root@192.168.20.123:/root/1.txt" ./
#######################
expect {
-re ".*es.*o.*" {
exp_send "yes\r"
exp_continue
}
-re ".*sword.*" {
exp_send "savari\r"
}
}
interact

