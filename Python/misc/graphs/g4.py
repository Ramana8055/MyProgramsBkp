#!/usr/bin/python
import sys
import os
database = (
    'dev',
    ['home', (
            'dir',
            ['ramana', (
                    '',
                    ['xyz', (
                            '',
                            'abc'
                        )
                    ],
                    ['xxx', (
                            '',
                            'def'
                        )
                    ]
                   )
            ]
         )
    ]
)

def permute(prefix, tree):
    def flatten(branch):
        #print 'flatten', branch
        results = [ ]
        if type(branch) is list:
            parts = [ ]
            for part in branch:
                if type(part) is basestring:
                    if part:
                        parts.append([part])
                else:
                    parts.append(flatten(part))

            index = map(lambda x: 0, parts)
            count = map(len, parts)
            #print 'combining', parts, index, count
            while True:
                line = map(lambda i: parts[i][index[i]],
                       range(len(parts)))
                line = '/'.join(line)
                #print '1:', line
                results.append( line )
                curIndex = len(parts)-1
                while curIndex >= 0:
                    index[curIndex] += 1
                    if index[curIndex] < count[curIndex]:
                        break
                    index[curIndex] = 0
                    curIndex -= 1
                if curIndex < 0:
                    break
        elif type(branch) is tuple:
            for option in branch:
                if type(option) is basestring:
                    if len(option):
                        #print '2:', option
                        results.append( option )
                else:
                    results.extend(flatten(option))
        else:
            #print '3:', branch
            results.append( branch )
        return results

    return map(lambda x: prefix + x, flatten(tree))


print permute("ls -l /",database)
