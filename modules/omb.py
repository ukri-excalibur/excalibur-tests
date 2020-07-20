import pandas as pd

# Example formats

# alltoall - note blank line at start!:
"""

# OSU MPI All-to-All Personalized Exchange Latency Test v5.6.2
# Size       Avg Latency(us)
1                      32.48
2                      32.85
...
"""

# bw:
"""
# OSU MPI Bandwidth Test v5.6.2
# Size      Bandwidth (MB/s)
1                       7.59
2                      14.52
...
"""

# bibw:
"""
# OSU MPI Bi-Directional Bandwidth Test v5.6.2
# Size      Bandwidth (MB/s)
1                       9.60
...
"""

# mbw_mr:
"""
# OSU MPI Multiple Bandwidth / Message Rate Test v5.6.2
# [ pairs: 1 ] [ window size: 64 ]
# Size                  MB/s        Messages/s
1                       7.79        7790845.03
2                      15.93        7962625.43
...
"""

OSU_OUTPUT_COLS = {
    '# OSU MPI All-to-All Personalized Exchange Latency Test': ('Size', 'Avg Latency(us)'),
    '# OSU MPI Bandwidth Test': ('Size', 'Bandwidth (MB/s)'),
    '# OSU MPI Bi-Directional Bandwidth Test': ('Size', 'Bandwidth (MB/s)'),
    '# OSU MPI Multiple Bandwidth / Message Rate Test': ('Size', 'MB/s', 'Messages/s'),
    '# OSU MPI Latency Test': ('Size', 'Latency (us)'),
    '# OSU MPI Allgather Latency Test': ('Size', 'Avg Latency(us)'),
    '# OSU MPI Allreduce Latency Test': ('Size', 'Avg Latency(us)'),
}

def read_omb_out(path):
    """ Read stdout from a multi-column OMB output file.
        
        Returns a pandas dataframe.
    """

    # NB: Some output files contain blank lines before # header lines.

    # work out file type:
    with open(path) as f:
        for line in f:
            if line.strip() == '':
                continue
            elif line.startswith('#'):
                test_type, test_ver = line.strip().split(' v')
                try:
                    header = OSU_OUTPUT_COLS[test_type]
                except KeyError:
                    raise KeyError('Do not know how to parse output for "%s"' % test_type)
                break
            else:
                raise ValueError('Unexpected non-blank/non-# line %r' % line)
            
    # read actual data:
    data = pd.read_csv(path, delim_whitespace=True, comment='#', names=header, header=0, skip_blank_lines=True)
    return data
    
if __name__ == '__main__':
    import sys
    d = read_omb_out(sys.argv[1])
    d = print(d)




