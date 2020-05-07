#!/usr/bin/env python

import subprocess as sp
import pprint

def get_node_info():
    """ Return a sequence of dicts, one per node.

        keys are as per `sinfo --Node --long`
    """
    nodeinfo = sp.run(['sinfo', '--Node', '--long'], capture_output=True).stdout.decode('utf-8') # encoding?

    nodes = []
    lines = nodeinfo.split('\n')
    header = lines[1].split() # line[0] is date/time
    for line in lines[2:]:
        line = line.split()
        if not line:
            continue
        nodes.append({})
        for ci, key in enumerate(header):
            nodes[-1][key] = line[ci]
    return nodes

if __name__ == '__main__':
    
    pprint.pprint(get_node_info())