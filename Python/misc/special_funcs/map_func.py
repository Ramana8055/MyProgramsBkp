#!/usr/bin/python -B

def f(x):
	return x*x*x

print map(f,range(0,25)) #print the output for every value(here cube of every value)

#Same thing can be done with:
print map(lambda x: x*x*x, range(0,25))


#map(function_name,arguments_to_be_passed)
