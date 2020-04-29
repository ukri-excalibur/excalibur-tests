#!/usr/bin/env python
""" Change a line in a file

    Usage:
        changeline.py path pattern newline

    wherere:
        path: path to file to change
        pattern: python regex to match a line
        newline:  replacement line (should not include \n)
    
    The first line matching `pattern` is entirely replaced with `newline`. 
"""
from __future__ import print_function
import sys, re
if __name__ == '__main__':
    path, pattern, newline = sys.argv[1:]
    with open(path) as fr:
        lines = fr.readlines()
    for ix, line in enumerate(lines):
        result = re.search(pattern, line)
        if result:
            if lines[ix] == newline + line[-1]:
                print('%s:%i matched %r, no change required' % (path, ix, pattern))
            else:    
                lines[ix] = newline + line[-1]
                print('%s:%i matched %r, replaced %r with %r' % (path, ix, pattern, line, lines[ix]))
                with open(path, 'w') as fw:
                    fw.write(''.join(lines))
                break