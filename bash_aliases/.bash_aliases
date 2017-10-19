#!/bin/bash

#*********************************************************
#                   Data Rates
#*********************************************************

DataRates() {
   echo -e "\tModulation     10MHz Datarate(MBPS)  20MHz Datarate(MBPS)"
   echo -e "\t1/2BPSK             3                     6"
   echo -e "\t3/4BPSK             4.5                   9"
   echo -e "\t1/2QPSK             6                     12"
   echo -e "\t3/4QPSK             9                     18"
   echo -e "\t1/2QAM16            12                    24"
   echo -e "\t3/4QAM16            18                    36"
   echo -e "\t2/3QAM64            24                    48"
   echo -e "\t3/4QAM64            27                    54"
}

Mac_to_link_local() {
   echo -e "\t1. Take the mac address: for example 52:74:f2:b1:a8:7f"
   echo -e "\t2. Throw ff:fe in the middle: 52:74:f2:ff:fe:b1:a8:7f"
   echo -e "\t3. Reformat to IPv6 notation 5274:f2ff:feb1:a87f"
   echo -e "\t4. Convert the first octet from hexadecimal to binary: 52 -> 01010010"
   echo -e "\t5. Invert the bit at index 6 (counting from 0): 01010010 -> 01010000"
   echo -e "\t6. Convert octet back to hexadecimal: 01010000 -> 50"
   echo -e "\t7. Replace first octet with newly calculated one: 5074:f2ff:feb1:a87f"
   echo -e "\t8. Prepend the link-local prefix: fe80::5074:f2ff:feb1:a87f"
}

## x="00deadbeef" #Match if this is a valid hex string
## if [[ "$x" =~ ^([[:xdigit:]]{6}) ]]; then echo match; else echo no match; fi

#Kernel Panic from cmd line
#echo c > /proc/sysrq-trigger

#To print the timestamp of when a command is executed
HISTTIMEFORMAT="%d/%m/%y %T "

h2d() {
   value=`echo $1| tr '[a-z]' '[A-Z]'`
   echo "ibase=16; $value"|bc
}

h2b() {
   value=`echo $1| tr '[a-z]' '[A-Z]'`
   echo "ibase=16;obase=2; $value"|bc
}

d2h() {
   echo "obase=16; $1"|bc
}

d2b() {
   echo "ibase=10;obase=2;$1"|bc
}

b2d() {
   echo "ibase=2;$1"|bc
}

b2h() {
   echo "ibase=2;obase=10000;$1"|bc
}

o2d() {
   echo "ibase=8;$1"|bc
}

d2o() {
   echo "obase=8;$1"|bc
}

h2o() {
   value=`echo $1|tr '[a-z]' '[A-Z]'`
   echo "ibase=16;obase=8;$value"|bc
}

o2h() {
   echo "ibase=8;obase=20;$1"|bc
}

Ping() {
   ping 192.168.20.$@
}

Set() {
#    PS1=${PS1}"\e]2;$@\a"
   printf '\e]2;%s\a' "$1";
}

alias ssh='ssh -X -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '
alias scp='scp -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null '

alias iv="vi"
alias sl="ls"
alias LS="ls"

alias Rpass="echo '1[8V:2<J5*W;2I16H1nu'"
alias Apass="echo '5@G3p9axINJA'"
alias Ppass="echo '6efre#ESpe'"

alias Cflags="echo '-Wall -Werror -Wshadow -Wundef -Wstrict-prototypes -Wunreachable-code -Wextra -Wno-unused-parameter'"

alias cl="echo -ne '\0033\0143'"

Scp() {
    scp -r -P51012 $1 root@192.168.20.$2:$3
}

Ssh() {
    ssh -p51012 root@192.168.20.$@
}

Speed() {
    if [ $# -ne 2 ]
    then
       echo "Use <conversion> <value>"
       echo "conversion can be k2m or m2k"
       return
    fi

    if [ "$1" = "k2m" ]
    then
       echo "scale=6;$2*5/18"|bc
       echo "m/s"
    elif [ "$1" = "m2k" ]
    then
       echo "scale=6;$2*18/5"|bc
       echo "km/h"
    else
       echo "Undefined conversion $2"
    fi
}

Vpn() {
    set +x
    cd /home/savari/Downloads/X/CRSSLconfig.tblk
    sudo cp resolv.conf /etc/
    set -x
    sleep 1
    sudo openvpn --config client.ovpn
    cd -
}

signed_value_in_hex() {
    /home/savari/Myprgms/c-prgms/conversions/signed_value_in_hex_based_on_bits $@
}

unsigned_to_signed() {
    /home/savari/Myprgms/c-prgms/conversions/unsigned_to_signed_based_on_bits $@
}

hex_to_char() {
    /home/savari/Myprgms/c-prgms/conversions/hex_to_char $@
}

wireshark() {
    /usr/bin/wireshark $@ 2>/dev/null 1>/dev/null &
}

PageClear() {
   sudo echo 1 > /proc/sys/vm/drop_caches
}

Dentry_and_Inode_Clear() {
   sudo echo 2 > /proc/sys/vm/drop_caches
}

PageClear_and_Dentry_and_Inode_Clear() {
   sudo echo 3 > /proc/sys/vm/drop_caches
}

Yesterday() {
   date --date="yesterday" +%Y-%m-%d
}

Camera() {
   cheese
}

export EDITOR=vim

#For Latex
#export PATH=${PATH}:/usr/local/texlive/2016/bin/x86_64-linux/

alias rm="trash-put"
alias rm -r="trash-put"
alias rm -rf="trash-put"

alias sp="ps"
alias PS="ps"

# Show only last directory in the prompt
PROMPT_DIRTRIM=1
clear
# xdotool search --name "Mozilla Firefox" set_window --name "Monkey" -->Renames Mozilla Firefox to Monkey
# Check here "http://askubuntu.com/questions/626505/how-do-i-permanently-change-window-titles"

mw_make() {
    make V=99 LOADADDR=0X12000000 "$@"
}

sw_make() {
    make V=99 LOADADDR=0X12000000 PLATFORM_TYPE:="SW1000" "$@"
}

nxp_make() {
    make V=99 LOADADDR=0X12000000 PLATFORM_TYPE:="SABRESD"  "$@"
}
