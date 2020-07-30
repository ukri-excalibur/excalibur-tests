#!/usr/bin/env python3
""" CLI utility to read performance log records.

    Usage:

        report.py TESTPATTERN
    
    where TESTPATTERN is a shell glob pattern matched against the last directory component of the perflog tree
    e.g.:
    - "Gromacs*" to get performance logs for all gromacs tests
    - "Gromacs_61k1" to get performance logs for a specific test

    This will query for the performance varible to display.
"""

import sys
sys.path.append('reframe')
import modules


if __name__ == '__main__':
    testname = sys.argv[-1]

    df = modules.utils.load_perf_logs('perflogs', test=testname, last=True)

    # have to filter to a single perf_var before reshaping:
    perf_vars = df['perf_var'].unique()
    if len(perf_vars) > 1:
        print('Loaded %i records. Perf_vars are:' % len(df.index))
        for ix, pv in enumerate(perf_vars):
            print('  %i: %s' % (ix, pv))
        perf_var_idx = input('Enter index of perf_var to display (default 0):') or '0'
        perf_var = perf_vars[int(perf_var_idx)]
    else:
        perf_var = perf_vars[0]
        print("Loaded %i records, only perf_vars is '%s'" % (len(df.index), perf_var))
    df = df.loc[df['perf_var'] == perf_var]

    # add a system:partition column:
    df['sys:part'] = df[['sysname', 'partition']].agg(':'.join, axis=1)
        
    # pivot to give a row per testname, column per system:partition, with values being selected perf_var
    df = df.pivot(index='testname', columns='sys:part', values='perf_value')

    print('perf_var:', perf_var)
    print(df)