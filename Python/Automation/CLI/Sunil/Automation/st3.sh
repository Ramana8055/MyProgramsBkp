#!/usr/bin/expect --

spawn scp -P 51012 -r  ppstest/. "root@192.168.20.123:/usr/local/bin" 
#######################
expect {
-re ".*es.*o.*" {
exp_send "yes\r"
exp_continue
}
-re ".*sword.*" {
exp_send "\r"
}
}
interact

