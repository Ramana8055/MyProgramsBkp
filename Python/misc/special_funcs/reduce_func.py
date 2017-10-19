#!/usr/bin/python
def add(x,y):return x+y
print reduce(add,range(1,11))  #here, first time it sends 1,2 next 1+2,3 next 1+2+3,4 and so on to add()

#similar to
print "\n",sum(range(1,11))
