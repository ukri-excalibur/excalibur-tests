# TODO:
# - compile wrf
# - download benchmark
# - run benchmark

import sys, os
import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append('.')
from modules.reframe_extras import scaling_config 
from modules.utils import parse_time_cmd

WRF_DIR = "$HOME/wrf-build-icc19-impi19-hsw" # TODO
BENCHMARK_DIR = "$HOME/CONUS-12km" # TODO

@rfm.parameterized_test(*scaling_config())
class WRF(rfm.RunOnlyRegressionTest):
    def __init__(self, part, num_tasks, num_tasks_per_node):
        self.num_tasks = num_tasks
        self.num_tasks_per_node = num_tasks_per_node
        self.num_nodes = int(self.num_tasks / self.num_tasks_per_node)
        self.time_limit = '3h'
        
        self.valid_systems = [part]
        self.valid_prog_environs = ['wrf']

        self.prerun_cmds = [
            'ln -sf {wrf_dir}/WRFV3.8.1/run/* .'.format(wrf_dir=os.path.expandvars(WRF_DIR)),
            'ln -sf {benchmark_dir}/* .'.format(benchmark_dir=os.path.expandvars(BENCHMARK_DIR)),  # must be second to overwrite namelist.input from run/
            "sed '/&dynamics/a \ use_baseparam_fr_nml = .t.' -i namelist.input", # NB this changes namelist.input into NOT a symlink!
            # not using pnetcdf so io_form_* being 2 already is correct
            'time \\',
        ]
        
        self.executable = 'wrf.exe'
        self.executable_opts = []

        self.postrun_cmds = [
            "grep 'Timing for main' rsl.error.0000 | tail -149 | awk '{print $9}' | awk -f stats.awk > timings.txt" # TODO: Replace this with python
        ] # TODO

        self.sanity_patterns = sn.all([
            sn.assert_found(r'wrf: SUCCESS COMPLETE WRF', 'rsl.error.0000'),
        ])
        self.perf_patterns = {
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
            'av_time_per_step': sn.extractsingle(r'\s+mean:\s+([\d\.]+)', 'timings.txt', 1, float),
        }
        self.reference = {
            '*': {
                'av_time_per_step': (0, None, None, 's'),
                'runtime_real': (0, None, None, 's'),
            }
        }
    
        self.tags |= {'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes}