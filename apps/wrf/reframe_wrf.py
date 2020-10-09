# TODO: Add docs
# TODO: Currently must set WRF_DIR in environment's variables (to parent of /RUN directory) - would be better to use a module?

import sys, os, urllib, string
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append('.')
from modules.wrf import extract_timings
from modules.reframe_extras import scaling_config 
from modules.utils import parse_time_cmd
from reframe.core.runtime import runtime

BENCHMARKS = {
    '12km': [
        {
            'url': 'http://www2.mmm.ucar.edu/WG2bench/conus12km_data_v3',
            'files': ['namelist.input', 'wrfbdy_d01', 'wrfrst_d01_2001-10-25_00_00_00'],
        },
    ],
    '2.5km': [
        {
            'url': 'http://www2.mmm.ucar.edu/WG2bench/conus_2.5_v3/1-RST/RST/',
            'files': ['rst_6hraa%s' % x for x in string.ascii_lowercase] \
                + ['rst_6hrab%s' % x for x in string.ascii_lowercase[0:7]]
        },
        {
            'url': 'http://www2.mmm.ucar.edu/WG2bench/conus_2.5_v3/2-9HR/',
            'files': ['namelist.input']
        },
        {
            'url': 'http://www2.mmm.ucar.edu/WG2bench/conus_2.5_v3/',
            'files': ['wrfbdy_d01.gz']
        },
    ],    
}

# For performance calculations - see https://www2.mmm.ucar.edu/wrf/WG2/benchv3/
TIMING_CONSTANTS = {
    '12km': {
        'model_timestep': 72,
        'gflops_factor': 0.418,
    },
    '2.5km': {
        'model_timestep': 15,
        'gflops_factor': 27.45,
    }
}

class WRF_download(rfm.RunOnlyRegressionTest):
    """ Download WRF benchmark files.
    
        These are large so only want to do this once per system. ReFrame cannot have test dependencies across partitions,
        hence this runs on all partitions. There is therefore a race condition here as the check/download is not atomic.
        TODO: FIXME somehow.
    """
    
    def __init__(self, benchmark):
        
        self.benchmark = benchmark

        self.valid_systems = ['*']
        self.valid_prog_environs = ['wrf']
        self.tags |= {self.benchmark, 'download'}

        self.time_limit = '1h'
        
        self.local = True
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
        for fileset in BENCHMARKS[self.benchmark]:
            for bench_file in fileset['files']:
                dst = os.path.join(benchdir, bench_file)
                src = fileset['url'] + '/' + bench_file
                if not os.path.exists(dst):
                    try:
                        urllib.request.urlretrieve(src, dst)
                    except:
                        print('ERROR retrieving %s' % src)
                        raise

@rfm.simple_test
class WRF_12km_download(WRF_download):
    def __init__(self):
        super().__init__('12km')

@rfm.simple_test
class WRF_2_5km_download(WRF_download):
    def __init__(self):
        super().__init__('2.5km')


class WRF_run(rfm.RunOnlyRegressionTest):
    def __init__(self, benchmark, part, num_tasks, num_tasks_per_node):
        """ Run a WRF benchmark using pre-downloaded files.
        
            Should be subclassed by a test decorated with
        
                @rfm.parameterized_test(*scaling_config())
            
            Args:
                benchmark: str, key in BENCHMARKS
                others: see `modules.reframe_extras.scaling_config()`
        """
        
        self.benchmark = benchmark
        self.num_tasks = num_tasks
        self.num_tasks_per_node = num_tasks_per_node
        self.num_nodes = int(self.num_tasks / self.num_tasks_per_node)
        self.time_limit = '3h' # TODO: change in child classes?
        self.benchdir = os.path.join(self.prefix, 'downloads', self.benchmark)
        # NB we do NOT set sourcesdir or readonly_files as we want to symlink in files ourselves
        
        self.valid_systems = [part]
        self.valid_prog_environs = ['wrf']

        self.executable = 'wrf.exe'
        self.executable_opts = []
        self.keep_files = ['rsl.error.0000']

        self.sanity_patterns = sn.all([
            sn.assert_found(r'wrf: SUCCESS COMPLETE WRF', 'rsl.error.0000'),
        ])

        self.model_timestep = TIMING_CONSTANTS[self.benchmark]['model_timestep']
        self.gflops_factor = TIMING_CONSTANTS[self.benchmark]['gflops_factor']
        
        self.perf_patterns = {
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
            'gflops': (self.model_timestep / sn.avg(sn.sanity_function(extract_timings)('rsl.error.0000'))) * self.gflops_factor
        }
        self.reference = {
            '*': {
                'runtime_real': (0, None, None, 's'),
                'gflops': (0, None, None, '/s'),
            }
        }
    
        self.tags |= {self.benchmark, 'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes, 'run'}

@rfm.parameterized_test(*scaling_config())
class WRF_12km_run(WRF_run):
    def __init__(self, part, num_tasks, num_tasks_per_node):
        """ Run the 12km CONUS benchmark """
        
        super().__init__('12km', part, num_tasks, num_tasks_per_node)
        self.depends_on('WRF_12km_download')
        
        self.prerun_cmds = [
            'ln -sf $WRF_DIR//run/* .', # TODO: use a module here instead of WRF_DIR
            'ln -sf {benchmark_dir}/* .'.format(benchmark_dir=self.benchdir),  # must be second to overwrite namelist.input from run/
            "sed '/&dynamics/a \ use_baseparam_fr_nml = .t.' -i namelist.input", # NB this changes namelist.input into NOT a symlink!
            # not using pnetcdf so io_form_* being 2 already is correct
            'time \\',
        ]

@rfm.parameterized_test(*scaling_config())
class WRF_2_5km_run(WRF_run):
    def __init__(self, part, num_tasks, num_tasks_per_node):
        """ Run the 2.5km CONUS benchmark """
        
        super().__init__('2.5km', part, num_tasks, num_tasks_per_node)
        #self.depends_on('WRF_2_5km_download') # TODO: DEBUG: FIXME:
        
        self.prerun_cmds = [ # from http://www2.mmm.ucar.edu/WG2bench/conus_2.5_v3/READ-ME.txt
            'ln -sf $WRF_DIR/run/* .', # TODO: use a module here instead of WRF_DIR
            'ln -sf {benchmark_dir}/* .'.format(benchmark_dir=self.benchdir),  # must be second to overwrite namelist.input from run/
            'cat rst_6hr* | gunzip -c > wrfrst_d01_2005-06-04_06_00_00',
            'gunzip --force wrfbdy_d01.gz', # --force reqd. as symlink
            r"sed -i '/&dynamics/a \ use_baseparam_fr_nml = .t.' namelist.input", # NB this changes namelist.input into NOT a symlink!
            r"sed -E -i 's/( io_form_[[:alpha:]]+ += )11,/\12,/' namelist.input", # replace all " io_form_* = 11," lines with with = 2
            'time \\',
        ]
