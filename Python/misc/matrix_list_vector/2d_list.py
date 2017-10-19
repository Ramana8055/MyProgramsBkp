#!/usr/bin/python

print [(x,y) for x in [1,2,3] for y in [3,1,4]]

#equivalent to
com=[]
for x in [1,2,3]:
	for y in [3,1,4]:
		com.append((x,y))
print com
print com[0][0]


print [(a,b) for a in [1,2,3] for b in [3,1,4] if a!=b ]
#equivalent to
com=[]
for a in [1,2,3]:
	for b in [3,1,4]:
		if a!=b:
			com.append((a,b))
print com
