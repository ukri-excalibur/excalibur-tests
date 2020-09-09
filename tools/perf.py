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
sys.path.extend(('reframe', '.'))
import modules

if __name__ == '__main__':
    testname = sys.argv[-1]

    df = modules.utils.load_perf_logs('perflogs', test=testname, last=True)

    # have to filter to a single perf_var before reshaping:
    perf_vars = df['perf_var'].unique()
    print('Loaded %i records. Select data to tabulate:' % len(df.index))
    for ix, pv in enumerate(perf_vars):
        print('  %i: %s' % (ix, pv))
    print('  %i: other (non-performance) variable' % (ix +1))
    var_idx = int(input('Enter a number (default 0):') or '0')
    if var_idx > ix:
        perf_var = None
        df = df.loc[df['perf_var'] == perf_vars[0]]
        for ix, pv in enumerate(df.columns):
            print('  %i: %s' % (ix, pv))
        var_idx = int(input('Enter a number (default 0):') or '0')
        pivot_vals = df.columns[var_idx]
    else:
        perf_var = perf_vars[var_idx]
        df = df.loc[df['perf_var'] == perf_var]
        pivot_vals = 'perf_value'

    # add a system:partition column:
    environs = df['environ'].unique()
    if len(environs) > 1:
        df['sys:part'] = df['sysname'] + ':' + df['partition'] + '/' + df['environ']
    else:
        df['sys:part'] = df['sysname'] + ':' + df['partition']
        
    # pivot to give a row per testname, column per system:partition, with values being selected item
    df = df.pivot(index='testname', columns='sys:part', values=pivot_vals)
    
    # if last part of '_'-delimited testname is numeric, then use it for sorting:
    # don't have key parameter for df.sort_index() in this version so have to create a new column
    testparts = [t.split('_') for t in df.index]
    if all(t[-1].isnumeric() for t in testparts):
        print('Have numeric testname suffix, sorting by that')
        df['_n'] = [int(v.rsplit('_', 1)[-1]) for v in df.index]    
        df = df.sort_values(by='_n')
        df.drop('_n', axis=1)

    if len(perf_vars) > 1:
        print('Showing', perf_var or pivot_vals)
    print(df)