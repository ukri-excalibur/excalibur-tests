import re

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
    '# OSU MPI All-to-All Personalized Exchange Latency Test': (int, float), # ('Size', 'Avg Latency(us)')
    '# OSU MPI Bandwidth Test': (int, float), # ('Size', 'Bandwidth (MB/s)')
    '# OSU MPI Bi-Directional Bandwidth Test': (int, float), # ('Size', 'Bandwidth (MB/s)')
    '# OSU MPI Multiple Bandwidth / Message Rate Test': (int, float, float), # ('Size', 'MB/s', 'Messages/s')
    '# OSU MPI Latency Test': (int, float), # ('Size', 'Latency (us)')
    '# OSU MPI Allgather Latency Test': (int, float), # ('Size', 'Avg Latency(us)')
    '# OSU MPI Allreduce Latency Test': (int, float), # ('Size', 'Avg Latency(us)')
}


def read_omb_out(path):
    """ Read stdout from a multi-column OMB output file.

        Returns a pandas dataframe.
    """
    # work out file type:
    rows = []
    with open(path) as f:
        for line in f:
            if line.strip() == '' or re.match('^(#|\d)', line) is None:
                # Skip empty lines or lines not starting with either `#` or a
                # number.
                continue
            elif line.startswith('#'):
                if line.startswith('# OSU MPI'):
                    # Line with benchmark name
                    test_type, test_ver = line.strip().split(' v')
                    try:
                        converters = OSU_OUTPUT_COLS[test_type]
                    except KeyError:
                        raise KeyError(f'Do not know how to parse output for "{test_type}"')
                else:
                    # Other commented out lines we don't need to parse, skip.
                    continue
            else:
                # Line starting with a number
                rows.append([f(v) for (f, v) in zip(converters, line.split())])
    return rows


if __name__ == '__main__':
    import sys
    rows = read_omb_out(sys.argv[1])
    for r in rows:
        print(r)
