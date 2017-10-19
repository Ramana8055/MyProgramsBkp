#!/usr/bin/python


#lambda is an ananymous function(function without name)

sequence=map(lambda x: x**x, range(10))
print sequence

#similarly
sequ=[]
s=lambda x: x**x
for i in range(10):
	sequ.append(s(i))
print sequ

#which is equivalent to 
seq=[x**x for x in range(10)]
print seq

#which is also equivalent to
sq=[]
for x in range(10):
	sq.append(x**x)
print sq
