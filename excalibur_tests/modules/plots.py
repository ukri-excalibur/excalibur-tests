import matplotlib.pyplot as plt

def add_roce_ib_factor(data, round=2):
    """ Add columns with roce / ib values to a dataframe produced by tabulate_last_perf() """
    # pair-up roce/ib columns:
    pairs = {} # tuple of system/partition parts with roce/ib replaced with '*' -> list of actual system:partition names
    for syspart in data.columns:
        sys, part = syspart.split(':')
        generic = [sys] + [('[roce/ib]' if p in ('ib', 'roce') else p) for p in part.split('-')]
        pairs.setdefault(tuple(generic), []).append(syspart)
    # now add columns:
    for generic, (c1, c2) in pairs.items():
        c_ib, c_roce = sorted([c1, c2]) # get IB first
        newcol = generic[0] + ':' + '-'.join(generic[1:])
        data[newcol] = (data[c_roce] / data[c_ib]).round(round)

def plot_perf_history(perf_df):
    """ Generate plots of performance history.
        
        Args:
            perf_df: A 'tidy' dataframe as returned by `modules.utils.load_perf_logs()`, indexed by log sequence.
        
        This produces 1x plot for each combination of `testname` and `perf_var` in `perf_df`.
        A series is generated for each "<sysname>-<partition>-<environ>" combination.

        Returns None
    """
    for test, data in perf_df.groupby('testname'):
        for perf_var, data in data.groupby('perf_var'):
            fig, ax = plt.subplots(nrows=1, ncols=1)
            # TODO: have lost minimalist labels of prev version, need to do that at this level
            # TODO: if multiple units (hope there won't be!) plot on 2ndary y-axes?
            y_labels = ', '.join(data.groupby('perf_unit').groups.keys()) # hopefully only one unit!
            for spe, data in data.groupby(['sysname', 'partition', 'environ']):
                ax.plot_date('completion_time', 'perf_value', 'o-', label='-'.join(spe), data=data)
            ax.set_title('%s: %s' % (test, perf_var))
            ax.set_xlabel('completion time')
            ax.set_ylabel(y_labels)
            ax.legend()
            ax.grid()
            fig.autofmt_xdate()

def tabulate_last_perf_vs(df, x_var, perf_var):
    """ Tablulate `x_var` vs the last record for `perf_var` per system/partition/environment.
    
        Manipulates a dataframe from `modules.utils.load_perf_logs()` for easy plotting and tabulation.
        
        Args:
            df: A 'tidy' dataframe as returned by `modules.utils.load_perf_logs()`, indexed by log sequence.
            x_var: str, label of column with values for e.g. x-axis of plot, or LH column of table
            perf_var: str, label of column with values for e.g. y-axis of plot, or values in table.
    
        Returns:
            A 'wide' dataframe with a column `x_var and all other columns being "<sysname>-<partition>-<environ>"
            for each combination. Values give the last `perf_var` found for each such combination.
    """
    
    # filter to rows for correct perf_var:
    df = df.loc[df['perf_var'] == perf_var]
    
    # keep only the LAST record in each system/partition/environment for each number of nodes
    df = df.sort_index().groupby(['sysname', 'partition', 'environ', x_var]).tail(1)
    
    # Add "case" column from combined system/partition/environment names:
    df['case'] = df[['sysname', 'partition', 'environ']].agg('-'.join, axis=1)
    
    # reshape to wide table:
    df = df.pivot(index=x_var, columns='case', values='perf_value')
    return df