import pandas as pd

def read_omb_out(path):
    """ Read stdout from a multi-column OMB output file.
        
        Assumes column names are in last # line.
        
        Returns a pandas dataframe.
    """

    # process comment lines to get header:
    with open(path) as f:
        for ix, line in enumerate(f):    
            if not line.startswith('#'):
                break
            headerline = line.strip('#').strip().split()
    
    # now join any units like "(foo)" back to their preceeding part:
    header = []
    for p in headerline:
        if p.startswith('('):
            header[-1] = header[-1] + ' ' + p
        else:
            header.append(p)
    
    # read actual data:
    data = pd.read_csv(path, delim_whitespace=True, comment='#', names=header, header=0, skip_blank_lines=True)
    return data
    
if __name__ == '__main__':
    import sys
    d = read_omb_out(sys.argv[1])
    d = print(d)




