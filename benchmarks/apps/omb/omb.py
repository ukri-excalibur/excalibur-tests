""" Performance test using OSU's Micro Benchmarks (OMB).

    See README for details.
"""

from collections import namedtuple
import re
import reframe as rfm
import reframe.utility.sanity as sn
import modules
from benchmarks.modules.omb import read_omb_out
from benchmarks.modules.utils import SpackTest

Metric = namedtuple('Metric', ['column_number', 'function', 'unit', 'label'])

class OSU_Micro_Benchmarks(SpackTest):

    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['default']
        self.exclusive_access = True
        self.perf_patterns = {} # something funny about reframe's attr lookup
        self.spack_spec = 'osu-micro-benchmarks@6.1'
        self.time_limit = '59m'
        self.add_metrics()

    def add_metrics(self):
        """ Add all Metrics from self.METRICS to sanity/performance/reference patterns """

        for metric in self.METRICS:
            self.sanity_patterns = sn.assert_found('# OSU MPI', self.stdout)
            self.perf_patterns[metric.label] = reduce(self.stdout, metric.column_number, metric.function)
            self.reference[metric.label] = (0, None, None, metric.unit) # oddly we don't have to supply the "*" scope key??


@sn.deferrable
def reduce(path, column_number, function):
    data = read_omb_out(path)
    col = [row[column_number] for row in data]
    return function(col)


@rfm.simple_test
class Osu_alltoall(OSU_Micro_Benchmarks):
    # 'column', 'function', 'unit', 'label'
    METRICS = [Metric(1, min, 'us', "min_av_latency")]

    def __init__(self):
        super().__init__()
        self.executable = 'osu_alltoall'
        self.tags = {'alltoall'}

    @run_after('setup')
    def setup_num_tasks(self):
        self.num_tasks_per_node = self.current_partition.processor.num_cpus
        self.num_tasks = 2 * self.num_tasks_per_node


@rfm.simple_test
class Osu_allgather(OSU_Micro_Benchmarks):
    METRICS = [Metric(1, min, 'us', "min_av_latency")]

    def __init__(self):
        super().__init__()
        self.executable = 'osu_allgather'
        self.tags = {'allgather'}

    @run_after('setup')
    def setup_num_tasks(self):
        self.num_tasks_per_node = self.current_partition.processor.num_cpus
        self.num_tasks = 2 * self.num_tasks_per_node


@rfm.simple_test
class Osu_allreduce(OSU_Micro_Benchmarks):

    METRICS = [Metric(1, min, 'us', "min_av_latency")]

    def __init__(self):
        super().__init__()
        self.executable = 'osu_allreduce '
        self.tags = {'allreduce'}

    @run_after('setup')
    def setup_num_tasks(self):
        self.num_tasks_per_node = self.current_partition.processor.num_cpus
        self.num_tasks = 2 * self.num_tasks_per_node


@rfm.simple_test
class Osu_bw(OSU_Micro_Benchmarks):

    METRICS = [Metric(1, max, 'MB/s', "max_bandwidth")]

    def __init__(self):

        super().__init__()
        self.executable = 'osu_bw'
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.tags = {'bw'}


@rfm.simple_test
class Osu_latency(OSU_Micro_Benchmarks):

    METRICS = [Metric(1, min, 'us', "min_latency")]

    def __init__(self):

        super().__init__()
        self.executable = 'osu_latency'
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.tags = {'latency'}


@rfm.simple_test
class Osu_bibw(OSU_Micro_Benchmarks):

    METRICS = [Metric(1, max, 'MB/s', "max_bandwidth")]

    def __init__(self):

        super().__init__()
        self.executable = 'osu_bibw'
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.tags = {'bibw'}
