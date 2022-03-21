"""
Base class definitions to enable consistent logging. Requires ReFrame v. 3.11.x
"""
import math
import reframe as rfm
from reframe.core.decorators import run_after


class DiRACTest(rfm.RegressionTest):

    num_total_cores = variable(int, loggable=True)
    num_omp_threads = variable(int, loggable=True)
    num_mpi_tasks = variable(int, loggable=True)
    num_mpi_tasks_per_node = variable(int, loggable=True)
    num_nodes = variable(int, loggable=True)

    @run_after('setup')
    def set_attributes_after_setup(self):
        """Set the required MPI and OMP ranks/tasks/threads"""

        self.num_mpi_tasks = self.num_tasks = max(self.num_total_cores//self.num_omp_threads, 1)

        try:
            cpus_per_node = self._current_partition.processor.num_cpus
            if cpus_per_node is None:
                raise AttributeError('Cannot determine the number of cores PP')

            self.num_nodes = math.ceil(self.num_mpi_tasks / cpus_per_node)

        except AttributeError:
            print('WARNING: Failed to determine the number of nodes required '
                  'defaulting to 1')
            self.num_nodes = 1

        self.num_mpi_tasks_per_node = math.ceil(self.num_mpi_tasks / self.num_nodes)
        self.num_tasks_per_node = self.num_mpi_tasks_per_node

        if self.num_total_cores // self.num_omp_threads == 0:
            print('WARNING: Had fewer total number of cores than the default '
                  f'number of OMP threads, using {self.num_total_cores} OMP '
                  f'threads')
            self.num_omp_threads = self.num_total_cores

        self.num_cpus_per_task = self.num_omp_threads
        self.variables = {
            'OMP_NUM_THREADS': f'{self.num_cpus_per_task}',
        }

        self.extra_resources = {
            'mpi': {'num_slots': self.num_mpi_tasks * self.num_cpus_per_task}
        }


"""
# The following is a possible sample of a strong scaling benchmark 
# ----------------------------------------------------------------------------- 

@rfm.simple_test
class StrongScalingBenchmark(GROMACSBenchmark):

    variant = parameter([4 * i for i in range(1, 5)])
    num_omp_threads = 4

    @run_before('setup')
    def set_total_num_cores(self):
        # A ReFrame parameter cannot also be a variable, thus assign
        # them to be equal at the start of the setup
        self.num_total_cores = self.variant
"""
