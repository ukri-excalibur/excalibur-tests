# examples of output - note that a single file *may* contain multiple
# benchmark results
#
# # Benchmarking Uniband
# # #processes = 2
# #---------------------------------------------------
#        #bytes #repetitions   Mbytes/sec      Msg/sec
#             0         1000         0.00      2189915
#
# # Benchmarking PingPong
# # #processes = 2
# #---------------------------------------------------
#        #bytes #repetitions      t[usec]   Mbytes/sec
#             0         1000         2.25         0.00

def read_imb_out(path):
    """ Read stdout from an IMB-MPI1 run.

        Returns a dict with:
            key:= int, total number of processes involved
            value:= pandas dataframe, i.e. one per results table. Columns as per table.

        If multiple results tables are present it is assumed that they are all the same benchmark,
        and only differ in the number of processes.
    """

    dframes = {}

    COLTYPES = { # all benchmark names here should be lowercase
        'uniband': (int, int, float, int), # #bytes #repetitions Mbytes/sec Msg/sec
        'biband': (int, int, float, int),
        'pingpong':(int, int, float, float), # #bytes #repetitions t[usec] Mbytes/sec
        'alltoall':(int, int, float, float, float) # #bytes #repetitions t_min[usec] t_max[usec] t_avg[usec]
    }

    with open(path) as f:
        for line in f:
            if line.startswith('# Benchmarking '):
                benchmark = line.split()[-1].lower()
                if benchmark not in COLTYPES:
                    raise ValueError(f'Do not know how to read {benchmark} benchmark in {path}')
                converters = COLTYPES[benchmark]
                line = next(f)
                expect = '# #processes = '
                if not line.startswith(expect):
                    raise ValueError(f'expected {expect}, got {nprocs_line}')
                n_procs = int(line.split('=')[-1].strip())
                while line.startswith('#'):
                    line = next(f) # may or may not include line "# .. additional processes waiting in MPI_Barrier", plus other # lines
                rows = []
                while True:
                    line = next(f).strip()
                    if line == '':
                        break
                    rows.append([f(v) for (f, v) in zip(converters, line.split())])
                dframes[n_procs] = rows
    return dframes

if __name__ == '__main__':
    import sys
    d = read_imb_out(sys.argv[1])
    for n, df in d.items():
        print(n)
