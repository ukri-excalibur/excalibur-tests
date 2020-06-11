import matplotlib.pyplot as plt
def plot_perf_history(perf_df):
    """ TODO: docstring """
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
