# TODO: Add docs
# TODO: Currently must set WRF_DIR in environment's variables (to parent of /RUN directory) - would be better to use a module?

import os
import re
import string
import sys
import urllib
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.utils import SpackTest


@sn.deferrable
def extract_timings(rsl_error_path):
    step_times = []
    with open(rsl_error_path) as f:
        for line in f:
            match = re.search(r'Timing for main: time \S+ on domain\s+\d+:\s+([\d.]+) elapsed seconds', line)
            if match is not None:
                step_times.append(float(match.group(1)))
    return step_times


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


class WRFBaseBenchmark(SpackTest):
    valid_systems = ['*']
    valid_prog_environs = ['default']
    spack_spec = 'wrf@3.9.1.1'

    time_limit = '3h'

    executable = 'wrf.exe'
    executable_opts = []
    keep_files = ['rsl.error.0000']

    num_cpus_per_task = 2
    num_tasks = required
    num_tasks_per_node = required

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]

    @run_after('setup')
    def setup_num_tasks(self):
        self.set_var_default(
            'num_tasks',
            self.current_partition.processor.num_cpus //
            min(1, self.current_partition.processor.num_cpus_per_core) //
            self.num_cpus_per_task)
        self.set_var_default('num_tasks_per_node',
                             self.current_partition.processor.num_cpus //
                             self.num_cpus_per_task)
        self.extra_resources = {
            'mpi': {'num_slots': self.num_tasks * self.num_cpus_per_task}
        }

    @run_after('setup')
    def download_benchmark(self):
        self.benchdir = os.path.join(self.prefix, 'downloads', self.benchmark)
        if not os.path.exists(self.benchdir):
            os.makedirs(self.benchdir)
        for fileset in BENCHMARKS[self.benchmark]:
            for bench_file in fileset['files']:
                dst = os.path.join(self.benchdir, bench_file)
                src = fileset['url'] + '/' + bench_file
                if not os.path.exists(dst):
                    try:
                        urllib.request.urlretrieve(src, dst)
                    except:
                        print('ERROR retrieving %s' % src)
                        raise

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.all([
            sn.assert_found(r'wrf: SUCCESS COMPLETE WRF', 'rsl.error.0000'),
        ])

    @run_before('performance')
    def set_perf_patterns(self):
        model_timestep = TIMING_CONSTANTS[self.benchmark]['model_timestep']
        gflops_factor = TIMING_CONSTANTS[self.benchmark]['gflops_factor']
        self.perf_patterns = {
            'gflops': (model_timestep / sn.avg(extract_timings('rsl.error.0000'))) * gflops_factor
        }


@rfm.simple_test
class WRF_2_5km_Benchmark(WRFBaseBenchmark):
    def __init__(self):
        self.benchmark = '2.5km'
        super().__init__()
        self.tags = {self.benchmark}
        self.benchdir = os.path.join(self.prefix, 'downloads', self.benchmark)
        self.prerun_cmds += [ # from http://www2.mmm.ucar.edu/WG2bench/conus_2.5_v3/READ-ME.txt
            'set -u', # make sure variables below are set
            'ln -sf ${WRF_HOME}/run/* .',
            f'ln -sf {self.benchdir}/* .',  # must be second to overwrite namelist.input from run/
            'cat rst_6hr* | gunzip -c > wrfrst_d01_2005-06-04_06_00_00',
            'gunzip --force wrfbdy_d01.gz', # --force reqd. as symlink
            r"sed -i '/&dynamics/a \ use_baseparam_fr_nml = .t.' namelist.input", # NB this changes namelist.input into NOT a symlink!
            r"sed -E -i 's/( io_form_[[:alpha:]]+ += )11,/\12,/' namelist.input", # replace all " io_form_* = 11," lines with with = 2
        ]
        self.reference = {
            '*': {
                'gflops': (0, None, None, 'GFLOPS/s'),
            }
        }


@rfm.simple_test
class WRF_12km_Benchmark(WRFBaseBenchmark):
    def __init__(self):
        self.benchmark = '12km'
        super().__init__()
        self.tags = {self.benchmark}
        self.benchdir = os.path.join(self.prefix, 'downloads', self.benchmark)
        self.prerun_cmds += [
            'set -u', # make sure variables below are set
            'ln -sf ${WRF_HOME}/run/* .',
            f'ln -sf {self.benchdir}/* .',  # must be second to overwrite namelist.input from run/
            "sed '/&dynamics/a \ use_baseparam_fr_nml = .t.' -i namelist.input", # NB this changes namelist.input into NOT a symlink!
            # not using pnetcdf so io_form_* being 2 already is correct
        ]
        self.reference = {
            '*': {
                'gflops': (0, None, None, 'GFLOPS/s'),
            }
        }
