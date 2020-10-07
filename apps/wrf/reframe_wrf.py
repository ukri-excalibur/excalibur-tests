# TODO: Add docs
# TODO: Currently must set WRF_DIR in environment's variables - would be better to use a module?

import sys, os, urllib
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append('.')
from modules.wrf import extract_timings
from modules.reframe_extras import scaling_config 
from modules.utils import parse_time_cmd
from reframe.core.runtime import runtime

BENCHMARKS = {
    '12km': {
        'url': 'http://www2.mmm.ucar.edu/WG2bench/conus12km_data_v3',
        'files': ['namelist.input', 'wrfbdy_d01', 'wrfrst_d01_2001-10-25_00_00_00'],
    },
}

@rfm.simple_test
class WRF_download(rfm.RunOnlyRegressionTest):
    """ Download WRF benchmark files.
    
        These are large so only want to do this once per system. ReFrame cannot have test dependencies across partitions,
        hence this runs on all partitions. There is therefore a race condition here as the check/download is not atomic.
        TODO: FIXME somehow.
    """
    
    def __init__(self):
        
        self.benchmark = '12km'

        self.valid_systems = ['*']
        self.valid_prog_environs = ['wrf']
        self.tags |= {self.benchmark, 'download'}

        self.time_limit = '1h'
        
        #self.local = True # see https://github.com/eth-cscs/reframe/issues/1511
        self.executable = 'echo'
        self.executable_opts = ['Done.']
        self.sanity_patterns = sn.all([
            sn.assert_found(r'Done.', self.stdout),
        ])
        
    @rfm.run_after('setup')
    def download_benchmark(self):
        """ Download benchmark to the tests download/{benchmark} - NB this must exist. """
        benchdir = os.path.join(self.prefix, 'downloads', self.benchmark)
        if not os.path.exists(benchdir):
            os.makedirs(benchdir)
        for bench_file in BENCHMARKS[self.benchmark]['files']:
            dst = os.path.join(benchdir, bench_file)
            src = BENCHMARKS[self.benchmark]['url'] + '/' + bench_file
            if not os.path.exists(dst):
                urllib.request.urlretrieve(src, dst)

@rfm.parameterized_test(*scaling_config())
class WRF(rfm.RunOnlyRegressionTest):
    def __init__(self, part, num_tasks, num_tasks_per_node):
        """ Run the 12km CONUS benchmark """
        self.num_tasks = num_tasks
        self.num_tasks_per_node = num_tasks_per_node
        self.num_nodes = int(self.num_tasks / self.num_tasks_per_node)
        self.time_limit = '3h'
        self.benchmark = '12km'
        self.benchdir = os.path.join(self.prefix, 'downloads', self.benchmark)
        # NB we do NOT set sourcesdir or readonly_files as we want to symlink in files ourselves
        
        self.depends_on('WRF_download')
        self.valid_systems = [part]
        self.valid_prog_environs = ['wrf']

        self.prerun_cmds = [
            'ln -sf $WRF_DIR/WRFV3.8.1/run/* .', # TODO: use a module here instead of WRF_DIR
            'ln -sf {benchmark_dir}/* .'.format(benchmark_dir=self.benchdir),  # must be second to overwrite namelist.input from run/
            "sed '/&dynamics/a \ use_baseparam_fr_nml = .t.' -i namelist.input", # NB this changes namelist.input into NOT a symlink!
            # not using pnetcdf so io_form_* being 2 already is correct
            'time \\',
        ]
        
        self.executable = 'wrf.exe'
        self.executable_opts = []
        self.keep_files = ['rsl.error.0000']

        self.sanity_patterns = sn.all([
            sn.assert_found(r'wrf: SUCCESS COMPLETE WRF', 'rsl.error.0000'),
        ])
        
        self.perf_patterns = {
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
            'gflops': (72.0 / sn.avg(sn.sanity_function(extract_timings)('rsl.error.0000'))) * 0.418
        }
        self.reference = {
            '*': {
                'runtime_real': (0, None, None, 's'),
                'gflops': (0, None, None, '/s'),
            }
        }
    
        self.tags |= {'12km', 'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes, 'run'}
