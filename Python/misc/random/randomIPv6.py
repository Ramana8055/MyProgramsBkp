#!/usr/bin/python -B
import random
from netaddr.ip import IPNetwork, IPAddress

#random.seed()
#ip_a = IPAddress('2001::cafe:0') + random.getrandbits(16)
ip_a = IPAddress(random.getrandbits(128))

ip_n = IPNetwork(ip_a)
ip_n.prefixlen = 64

print ip_a
print ip_n
