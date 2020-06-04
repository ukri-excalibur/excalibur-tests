''' Playground for seeing what reframe can do.

    Run using something like:
        
        conda activate hpc-tests
        reframe/bin/reframe -C reframe-settings.py -c gromacs-2016.4/ --run # --performance-report

 TODO:
'''

import reframe as rfm
import reframe.utility.sanity as sn
import os, sys, urllib
sys.path.append('.')
import reframe_extras

from reframe.core.logging import getlogger

@rfm.simple_test
class Gromacs_SmallBM(rfm.RunOnlyRegressionTest):
    def __init__(self):
        """ Run Archer 'small' (single-node) Gromacs benchmark.

            Based on https://github.com/hpc-uk/archer-benchmarks/blob/master/apps/GROMACS/1400k-atoms/run/CSD3-Skylake/submit.slurm

            TODO:
            - add perf and sanity patterns
            - parameterise for different numbers of cores
        """

        self.valid_systems = ['*']
        self.valid_prog_environs = ['spack-gnu7-openmpi4']

        num_nodes = 1
        cpu_factor = 0.5 # because SMT is on on alaska
        max_cpus = int(reframe_extras.slurm_node_info()[0]['CPUS']) # 0: arbitrarily use first nodes info
        num_tasks = int(max_cpus * cpu_factor)
        casename = 'benchmark'
        resfile=casename
        
        self.sourcesdir = os.path.join(self.prefix, 'downloads') # i.e. downloads/ will be alongside this file
        self.executable = 'gmx_mpi'
        self.executable_opts = ['mdrun', '-s', '%s.tpr' % casename, '-g', resfile, '-noconfout']
        self.num_tasks = num_tasks
        self.num_tasks_per_node = int(num_tasks / num_nodes)
        self.exclusive_access = True
        self.time_limit = None # TODO: set this to something reasonable??

        self.keep_files = ['benchmark.log']
        self.sanity_patterns = sn.assert_found(r'Performance:', self.stderr)
        self.perf_patterns = None # TODO: FIXME:

        # TODO:
        # set norequeue?
        # use openmp?
    
    @rfm.run_before('run')
    def download_benchmark(self):
        """ Download benchmark file from Archer benchmarks gitlab.
        
            NB: This saves it to a persistent location defined by `self.sourcesdir` - reframe will then copy it into the staging dir.
        """

        benchmark_url = 'https://github.com/hpc-uk/archer-benchmarks/blob/master/apps/GROMACS/1400k-atoms/input/benchmark.tpr?raw=true'
        if not os.path.exists(self.sourcesdir):
            os.makedirs(self.sourcesdir, exist_ok=True)
        dest = os.path.join(self.sourcesdir, 'benchmark.tpr')
        if not os.path.exists(dest):
            urllib.request.urlretrieve(benchmark_url, dest)
    
    @rfm.run_before('run')
    def no_run(self):
        # fake the executable using bash's "noop" builtin - NB this needs to be in saved_output_dir too:
        self.executable = "./noop.sh"

    @rfm.run_after('run')
    def debug_postpro(self):
        """ Fakes a run to allow testing from after a run.

            Requires a saved run directory
        """

        saved_output_dir = 'Gromacs_SmallBM' # relative to this test directory

        saved_output_path = os.path.join(self.prefix, saved_output_dir)
        
        # check saved output path exists:
        if not os.path.exists(saved_output_path) or not os.path.isdir(saved_output_path):
            raise ValueError("saved output path %s does not exist or isn't a directory!" % os.path.abspath(saved_output_path))
        
        # copy files to stage dir:
        import distutils.dir_util
        distutils.dir_util.copy_tree(saved_output_path, self.stagedir)
                