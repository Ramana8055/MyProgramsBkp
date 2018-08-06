#!/usr/bin/python
matrix=[ [1,2,3],
     [3,4,5],
     [6,7,8],
]

#transpose
print zip(*matrix)

#similar to
row=[[row[i] for row in matrix] for i in range(3)]
print row

#equivalent to
transpose=[]
for i in range(3):
    transpose.append([row[i] for row in matrix])
print transpose

#also equivalent to
trans=[]
for i in range(3):
    trans_row=[]
    for row in matrix:
        trans_row.append(row[i])
    trans.append(trans_row)
print trans
