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
    environs = df['environ'].unique()
    if len(environs) > 1:
        df['sys:part'] = df['sysname'] + ':' + df['partition'] + '/' + df['environ']
    else:
        df['sys:part'] = df['sysname'] + ':' + df['partition']
        
    # pivot to give a row per testname, column per system:partition, with values being selected perf_var
    df = df.pivot(index='testname', columns='sys:part', values='perf_value')

    # if last part of '_'-delimited testname is numeric, then use it for sorting:
    # don't have key parameter for df.sort_index() in this version so have to create a new column
    testparts = [t.split('_') for t in df.index]
    if all(t[-1].isnumeric() for t in testparts):
        print('Have numeric testname suffix, sorting by that')
        df['_n'] = [int(v.rsplit('_', 1)[-1]) for v in df.index]    
        df = df.sort_values(by='_n')
        df.drop('_n', axis=1)

    if len(perf_vars) > 1:
        print('perf_var:', perf_var)
    print(df)