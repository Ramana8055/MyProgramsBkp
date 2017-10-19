#!/usr/bin/python -B

def f(x):
    return x%3==0

print filter(f,range(0,30)) #print all the values within range that are true(x%3 is 0)

#filter(function_name,args_to_that_function)

print filter(lambda x:(x%3==0), range(30))
