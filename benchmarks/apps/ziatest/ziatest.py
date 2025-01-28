import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest


@rfm.simple_test
class ZiatestBenchmark(SpackTest):
    valid_systems = ['-gpu']
    valid_prog_environs = ['default']
    spack_spec = 'ziatest'
    num_tasks = 1
    num_tasks_per_node = 1
    cpus_per_task = 1
    # We don't call `ziatest` but do the call to `ziaprobe` directly, as we
    # better control the MPI launcher and its arguments.
    executable = 'ziaprobe'
    executable_opts = [
        # This requires using coreutil's `date`, but that
        # should be available on most clusters.
        '$(date +"%s %6N")',
        str(num_tasks),
    ]
    time_limit = '10m'

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'Time test was completed in', self.stderr)

    @run_before('sanity')
    def set_perf_patterns(self):

        def time_to_sec(s):
            minutes, seconds = s.split(":")
            return int(minutes) * 60 + int(seconds)

        self.perf_patterns = {
            'time': sn.extractsingle(
                r'Time test was completed in +(\d+:\d+) +min:sec',
                self.stderr, 1, time_to_sec)
        }
