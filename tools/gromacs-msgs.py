#!/usr/bin/env python

import glob, pprint, re

GROMACS_ERR_PATH = 'output/csd3/cclake-*-gcc9-ompi3-ucx/gromacs/*/*.err'

PATTERNS = (
    r'(step \d+ .* dynamic load balancing)',
    r'(\d+ % of the run time was [\w\s]+)',
)

if __name__ == '__main__':
    paths = glob.glob(GROMACS_ERR_PATH)

    for p in paths:
        descr = p.split('/')[4]
        _, _, atoms, _, _, _, interconnect, _, _, _, nprocs, nppn = descr.split('_')
        with open(p) as f:
            for line in f:
                for pat in PATTERNS:
                    m = re.search(pat, line)
                    if m:
                        print(','.join((atoms, interconnect, nprocs, nppn, m.group(0))))

    #pprint.pprint(descr)