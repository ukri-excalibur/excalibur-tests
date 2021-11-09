""" Motorbike benchmark using OpenFOAM.

    See README.md for details.

    Note that the provided benchmark run script is not used and instead its functionality has been implemented using ReFrame.

    TODO: Move to use newer scaling_config().
"""

import sys
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append('.')
from modules.reframe_extras import scaling_config
from modules.utils import parse_time_cmd, identify_build_environment


@rfm.parameterized_test(*scaling_config())
class Openfoam_Mbike(rfm.RegressionTest):

    def __init__(self, part, n_tasks, n_tasks_per_node):

        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.build_system = 'Spack'

        self.num_tasks_per_node = n_tasks_per_node
        self.num_tasks = n_tasks
        self.num_nodes = int(n_tasks / n_tasks_per_node)
        self.tags = {'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes}

        self.sourcesdir = 'downloads'
        self.exclusive_access = True
        self.time_limit = '1h'

        self.prerun_cmds = [
            'tar --strip-components 2 -xf Motorbike_bench_template.tar.gz bench_template/basecase',
            './Allclean', # removes logs, old timehistories etc just in case

            # set domain decomposition:
            # using 'scotch' method means simpleCoeffs is ignored so it doesn't need to match num_tasks:
            'sed -i -- "s/method .*/method          scotch;/g" system/decomposeParDict',
            'sed -i -- "s/numberOfSubdomains .*/numberOfSubdomains %i;/g" system/decomposeParDict' % self.num_tasks,

            # remove streamlines:
            'sed -i -- \'s/    #include "streamLines"//g\' system/controlDict',
            'sed -i -- \'s/    #include "wallBoundedStreamLines"//g\' system/controlDict',

            # fix location of mesh quality defaults (needed for v6+?)
            "sed -i -- 's|caseDicts|caseDicts/mesh/generation|' system/meshQualityDict",

            './Allmesh', # do meshing

            'time \\', # want to run mpi task under time
        ]
        # could also check:
        #$ ompi_info -c | grep -oE "MPI_THREAD_MULTIPLE[^,]*"
        # MPI_THREAD_MULTIPLE: yes

        self.executable = 'simpleFoam'
        self.executable_opts = ['-parallel']

        self.keep_files = ['log.snappyHexMesh', 'log.blockMesh', 'log.decomposePar']

        result = sn.extractall(
            r'time step continuity errors : '
            r'\S+\s\S+ = \S+\sglobal = (?P<res>-?\S+),',
            self.stdout, 'res', float)
        # NB: `time` outputs to stderr so can't assume that should be empty
        self.sanity_patterns = sn.all([
            # ensure meshing finished ok:
            sn.assert_found('End', 'log.blockMesh'),
            sn.assert_found('End', 'log.decomposePar'),
            sn.assert_found('Finished meshing without any errors', 'log.snappyHexMesh'),

            # ensure simpleFoam finished ok:
            sn.assert_found('Finalising parallel run', self.stdout),
            sn.assert_not_found('FOAM FATAL ERROR', self.stdout),
            sn.assert_not_found('FOAM FATAL ERROR', self.stderr),

            # ensure continuity errors small enough - copied from
            # https://github.com/eth-cscs/reframe/blob/0a4dc5207b35c737861db346bd483fd4ac202846/cscs-checks/apps/openfoam/check_openfoam_extend.py#L56
            sn.all(
                sn.map(lambda x: sn.assert_lt(abs(x), 5.e-04), result)
            ),
        ])

        self.perf_patterns = {
            # from openfoam output:
            'ExecutionTime': sn.extractall(r'ExecutionTime = ([\d.]+) s  ClockTime = ([\d.]+) s', self.stdout, 1, float)[-1],
            'ClockTime': sn.extractall(r'ExecutionTime = ([\d.]+) s  ClockTime = ([\d.]+) s', self.stdout, 2, float)[-1],
            # from `time`:
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
        }
        self.reference = {
            '*': {
                'ExecutionTime': (0, None, None, 's'),
                'ClockTime': (0, None, None, 's'),
                'runtime_real': (0, None, None, 's'),
            }
        }

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.environment = identify_build_environment(
            self.current_system.name)
        self.build_system.specs = ['openfoam']
