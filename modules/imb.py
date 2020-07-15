import pandas as pd

# examples of output:
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
        
        Returns a series of pandas dataframes, one output table.
        Each contains the columns in the output plus a column '#processes'.
    """

    dframes = []

    COLTYPES = {
        'uniband': (int, int, float, int),
        'biband': (int, int, float, int),
        'pingpong':(int, int, float, float),
    }

    with open(path) as f:
        for line in f:
            if line.startswith('# Benchmarking '):
                benchmark = line.split()[-1].lower()
                converters = COLTYPES[benchmark]
                line = next(f)
                expect = '# #processes = '
                if not line.startswith(expect):
                    raise ValueError('expected %s, got %s' % (expect, nprocs_line))
                n_procs = int(line.split('=')[-1].strip())
                while line.startswith('#'):
                    line = next(f) # may or may not be line ".. additional processes waiting in MPI_Barrier"
                cols = line.strip().split()
                rows = []
                while True:
                    line = next(f).strip()
                    if line == '':
                        break
                    rows.append(f(v) for (f, v) in zip(converters, line.split()))
                data = pd.DataFrame(rows, columns=cols)
                data['#processes'] = n_procs
                dframes.append(data)
                #print('MAX %s: %s' % (n_procs, max(data['Mbytes/sec'])))
    return dframes

if __name__ == '__main__':
    import sys
    d = read_imb_out(sys.argv[1])
    for df in d:
        print(df)
        print()
