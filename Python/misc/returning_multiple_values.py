#!/usr/bin/python

def select_choice():
    return 1,2,3,4,5

d=select_choice() #catch all return values into an array

print d

print d[0],d[1]

#underscore means you are ignoring the first return type
_,e=select_choice() #ignore first value

print e

f=select_choice()[0] #Read first returned value
g=select_choice()[1] #Read second returned value

print f
print g

#h, *b, x=select_choice() #*b reads everything except first and last WORKS ONLY IN PYTHON 3
