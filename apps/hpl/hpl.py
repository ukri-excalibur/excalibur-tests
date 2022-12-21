import os.path as path
import sys
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append(path.join(path.dirname(__file__), '..', '..'))
from modules.utils import SpackTest

@rfm.simple_test
class Hpl(SpackTest):
    """High Performance Linpack - Intel optimised version."""

    valid_systems = ['*']
    valid_prog_environs = ['default']
    # self.prefix so relative to test dir, not pwd The `xhpl_intel64_dynamic` binary
    # dynamically links to Intel MPI, so we always have to specify the Intel MPI
    # dependency.  However note that `intel-mkl` in Spack doesn't depend on `mpi`, so we
    # have to specify `intel-mpi` as a separate dependency (e.g., can't use `intel-mkl
    # ^intel-mpi` as spec).
    spack_spec = 'intel-mkl intel-mpi'

    num_tasks_per_node = 1

    # NB num tasks etc done after setup
    exclusive_access = True
    time_limit = '1h'
    executable = '$MKLROOT/benchmarks/mp_linpack/xhpl_intel64_dynamic'

    config_dir = variable(str, value='')

    # Dictionary of reference values, indexed by number of tasks.
    full_reference = {
        1: {
            'csd3-skylake': {
                'Gflops': (2000, -0.2, None, 'Gflops'),
            },
            'csd3-icelake': {
                'Gflops': (4500, -0.2, None, 'Gflops'),
            },
        },
    }

    @run_after('setup')
    def set_sourcesdir(self):
        if self.config_dir:
            self.sourcesdir = self.config_dir
        else:
            self.sourcesdir = path.join(path.dirname(__file__), self.current_system.name, str(self.num_tasks))


    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]


    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.all([
            sn.assert_found('End of Tests.', self.stdout),
            sn.assert_found('0 tests completed and failed residual checks', self.stdout),
        sn.assert_found('0 tests skipped because of illegal input values.', self.stdout)
        ])

    @run_before('performance')
    def set_perf_patterns(self):

        self.perf_patterns = {
            # e.g.:
            # T/V                N    NB     P     Q               Time                 Gflops
            # --------------------------------------------------------------------------------
            # WR11C2R4       46080   192    16    32              12.91             5.0523e+03

            # see hpl-2.3/testing/ptest/HPL_pdtest.c:{219,253-256} for pattern details - assuming Intel is the same
            'Gflops': sn.extractsingle(r'^W[R|C]\S+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d[\d.]+\s+(\d[\d.eE+]+)', self.stdout, 1, float),
        }
        # If we have a reference for current combination of system + number of
        # tasks, use it, otherwise default to generic empty reference.
        if self.num_tasks in self.full_reference.keys() and self.current_system.name in self.full_reference[self.num_tasks].keys():
            self.reference = self.full_reference[self.num_tasks]
        else:
            self.reference = {
                '*': {
                    'Gflops': (None, None, None, 'Gflops'),
                }
            }

