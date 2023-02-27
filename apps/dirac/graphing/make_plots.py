import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from datetime import datetime
from glob import glob
from typing import Optional
from matplotlib.ticker import FormatStrFormatter


this_dir = os.path.dirname(os.path.abspath(__file__))


class ReFrameBenchmarkLine:
    """A single benchmark present in a ReFrame perflog file"""

    def __init__(self, line: Optional[str]):

        self._raw_line = line

        self.datetime = None                  # e.g.  2022-03-24T21:01:12
        self.reframe_version = None           # e.g.  3.10.0
        self.name = None                      # e.g.  RamsesMPI_strong_128
        self.system = None                    # e.g.  dial
        self.partition = None                 # e.g.  slurm-mpirun
        self.dependencies = None              # e.g.  intel-oneapi-openmpi
        self.num_tasks = None                 # e.g.  128
        self.num_cpus_per_task = None         # e.g.  2
        self.num_tasks_per_node = None        # e.g.  128
        self.num_total_cpus = None            # e.g.  256

        self.metric_name = None               # e.g.  Total elapsed time
        self.metric_value = None              # e.g.  41.51
        self.metric_reference = None          # e.g.  0

        if line is not None:
            self._set_attributes(line)

    @property
    def values(self) -> list:
        """Create a data frame from all the public attributes in this class"""
        return [v for k, v in self.__dict__.items() if not k.startswith('_')]

    @classmethod
    def column_names(cls) -> list:
        """Names of the columns in this log line"""

        tmp = cls(line=None)

        return [k for k in tmp.__dict__.keys() if not k.startswith('_')]

    def _set_attributes(self, line: str) -> None:
        """Set all the extractable attributes from the log file"""

        self.datetime = datetime.fromisoformat(line.split('|')[0])
        self.reframe_version = self._extract_reframe_version()
        self._set_name_and_system()
        self.num_tasks = int(self._value_of('num_tasks'))
        self.num_cpus_per_task = self._extract_num_cpus_per_task()
        self.num_tasks_per_node = int(self._value_of('num_tasks_per_node'))
        self.num_total_cpus = self.num_tasks * self.num_cpus_per_task

        self.metric_name = self._extract_metric_name()
        self.metric_value = float(self._value_of(self.metric_name))
        self.metric_reference = float(self._extract_metric_ref())

    def _set_name_and_system(self) -> None:
        """Set the name and system specifics from the appropriate section"""

        section = self._raw_line.split('|')[2]
        self.name = section.split()[0]

        self.system, self.partition = None, ''

        for a in (' on ', ' @'):
            for b in (' using ', ':'):
                try:
                    string = section.split(a)[1].split(b)[0]

                    if ':' in string:
                        self.system, self.partition = string.split(':')
                    else:
                        self.system = string

                except IndexError:
                    continue

        delim = ' using ' if 'using' in section else '+'
        self.dependencies = section.split(delim)[1]

        return None

    def _extract_metric_name(self) -> str:
        return self._raw_line.split('|')[-3].split('=')[0]

    def _value_of(self, s) -> str:
        return next(x.split('=')[1] for x in self._raw_line.split('|') if s in x)

    def _extract_num_cpus_per_task(self):
        val = self._value_of('num_cpus_per_task')
        return 1 if val == 'null' else int(val)

    def _extract_reframe_version(self) -> str:
        return self._raw_line.split('|')[1].split()[1].split('+')[0]

    def _extract_metric_ref(self) -> str:
        return self._raw_line.split('|')[-2].split()[0].split('=')[1]


class ReFrameLogFile:
    """A ReFrame generated perflog file containing benchmark(s)"""

    def __init__(self, file_path: str):

        self.file_path = self._validated(file_path)
        self.rows = []

        for line in open(self.file_path, 'r'):
            self.rows.append(ReFrameBenchmarkLine(line).values)

    @staticmethod
    def _validated(file_path: str) -> str:

        if not file_path.endswith('.log') or not os.path.exists(file_path):
            raise ValueError('File did not exist, or wasn\'t a .log')

        return file_path


def create_full_data_frame(relative_root: str) -> pd.DataFrame:
    """
    Create a pandas dataframe comprised of all the ReFrame benchmark data that
    can be found from a root directory relative to the path of this file and
    the sub directories within.

    ---------------------------------------------------------------------------
    Arguments:
        relative_root: Directory path relative to this one. For example: '.'
                       is the directory where this file is present and '..' one
                       directory up from this one

    Returns:
        (pd.DataFrame): Full data frame
    """
    rows = []

    for file_path in glob(os.path.join(this_dir, relative_root, '**/*.log'),
                          recursive=True):

        try:
            log_file = ReFrameLogFile(file_path)
            rows += log_file.rows

        except (ValueError, IndexError):
            print(f'Failed to parse {file_path}')

    return pd.DataFrame(rows, columns=ReFrameBenchmarkLine.column_names())


def correct_num_cpus_per_task(_df: pd.DataFrame) -> None:
    """
    Ensure the number of cpus per task is "correct". This applies to the
    perflogs generated before 08/06/2022, which did not save the correct
    value of num_cpus_per_task
    """
    system_name_to_num_cpus = {'cosma8': 128,
                               'dial': 128,
                               'csd3': 76}

    for i, row in _df.iterrows():
        for system in ('dial', 'cosma8', 'csd3'):

            if system == row['system']:
                n = int(system_name_to_num_cpus[system]
                        / row['num_tasks_per_node'])

                _df.loc[i, 'num_cpus_per_task'] = n

    return None


# ############################ Plotting specific ##############################

mpl.rcParams['axes.labelsize'] = 15
mpl.rcParams['lines.linewidth'] = 1
mpl.rcParams['lines.markersize'] = 5
mpl.rcParams['xtick.labelsize'] = 14
mpl.rcParams['ytick.labelsize'] = 14
mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['ytick.direction'] = 'in'
mpl.rcParams['xtick.top'] = True
mpl.rcParams['ytick.right'] = True
mpl.rcParams['axes.linewidth'] = 1.2

colors = ('tab:blue', 'tab:orange')


def rows_where_the_name_contains(*args) -> pd.DataFrame:
    return df[[all(a.lower() in str(name).lower() for a in args)
               for name in df['name']]]


def rows_where_the_name_contains_and_system_equals(string, system):
    rows = rows_where_the_name_contains(string)
    return rows[[s == system for s in rows['system']]]


def save_plot(filename):
    """Save the plot with a tight layout"""

    plt.legend()
    plt.tight_layout()
    plt.savefig(filename, transparent=True)
    return plt.close()


def plot_scaling_benchmark(rows,
                           color='tab:blue',
                           filename=None,
                           fig=None,
                           label=None):
    """Plot a scaling benchmark given a set of pandas df rows and a filename"""

    if fig is None:
        plt.figure(figsize=(8.4, 4))

    if len(rows) == 0:
        print(f'Failed to plot {filename}. Had no data')
        return

    xs_ys = [(x, y) for x, y in
             sorted(zip(rows['num_total_cpus'], rows['metric_value']))]

    ys = np.array([y for _, y in xs_ys])

    plt.plot([x for x, _ in xs_ys],
             ys/min(ys),
             lw=1.5,
             color=color,
             marker='o',
             ms=8,
             markerfacecolor='white',
             markeredgecolor=color,
             label=label)

    plt.xlabel('# cores')
    # plt.ylabel(list(rows['metric_name'])[0])
    plt.ylabel('Relative metric')
    plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

    if filename is not None:
        save_plot(filename)

    return None


def plot_trove_strong_scaling_benchmarks():

    fig = plt.figure(figsize=(8.4, 4))

    for input_val in ('12N', '16N'):
        for i, system in enumerate(('dial', 'csd3')):

            rows = rows_where_the_name_contains_and_system_equals(
                f'TROVE_{input_val}', system
            )

            plot_scaling_benchmark(
                rows=rows,
                fig=fig,
                color=colors[i],
                label=system
            )

        save_plot(f'build/trove_strong_{input_val}.pdf')

    return None


def plot_ramses_and_sphng_scaling_benchmarks():

    for scaling_type in ('weak', 'strong'):
        for name in ('Ramses', 'Sphng'):

            fig = plt.figure(figsize=(8.4, 4))

            for i, system in enumerate(('dial', 'csd3')):

                rows = rows_where_the_name_contains(name, scaling_type)
                rows = rows[[s == system for s in rows['system']]]

                plot_scaling_benchmark(
                    rows=rows,
                    label=system,
                    fig=fig,
                    color=colors[i]
                )

            save_plot(f'build/{name}_{scaling_type}.pdf')

    return None


if __name__ == '__main__':

    df = create_full_data_frame(relative_root='..')
    correct_num_cpus_per_task(df)
    df.to_csv('all_data.csv')

    plot_ramses_and_sphng_scaling_benchmarks()
    plot_trove_strong_scaling_benchmarks()
