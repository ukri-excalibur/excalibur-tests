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
    """ Read stdout from an IMB-MPI1 run. Note this may only contain ONE benchmark.
        
        Returns a pandas dataframe.
    """

    COLTYPES = {
        'uniband':(int, int, float, int),
        'biband':(int, int, float, int),
        'pingpong':(int, int, float, float),
    }

    # process comment lines to get header:
    with open(path) as f:
        for ix, line in enumerate(f):    
            if line.strip().startswith('#bytes '):
                header = line.strip().split()
                break

    # read actual data:
    data = pd.read_csv(path, delim_whitespace=True, comment='#', names=header, header=0, skip_blank_lines=True)
    return data
    

if __name__ == '__main__':
    import sys
    d = read_imb_out(sys.argv[1])
    d = print(d)
