""" Performance test using Gromacs molecular dynamics code: http://www.gromacs.org/

    Runs benchmarks from HECBioSim: http://www.hecbiosim.ac.uk/benchmarks
    - 61K atom system - 1WDN Glutamine-Binding Protein
    - 1.4M atom system - A Pair of hEGFR Dimers of 1IVO and 1NQL
    - 3M atom system - A Pair of hEGFR tetramers of 1IVO and 1NQL

    Run using e.g.:
        
        cd hpc-tests
        conda activate hpc-tests
        reframe/bin/reframe -C reframe_config.py -c gromacs/ --run --performance-report
"""

import reframe as rfm
import reframe.utility.sanity as sn
import os, sys, urllib, shutil
sys.path.append('.')
from modules import reframe_extras

from reframe.core.logging import getlogger

class Gromacs_HECBioSim(rfm.RunOnlyRegressionTest, reframe_extras.CachedRunTest):
    """ Base class for HECBioSim Gromacs benchmarks.

        Runs for environments named "gromacs" only.

        This sets parameters common to all benchmarks and handles download/unpacking benchmark files.

        Set `self.use_cache=True` in derived instances to re-run results processing without actually running
        gromacs again, e.g. during debugging. See `reframe_extras.CachedRunTest` for details.
        
        Args:
            casename: directory name from the HECBioSim benchmark download, one of:
                1400k-atoms  20k-atoms  3000k-atoms  465k-atoms  61k-atoms
            logfile: log file name (-g option for `gmx mdrun`)
    """
    def __init__(self, casename):
        
        self.casename = casename
        self.logfile = casename + '.log'
        
        self.valid_systems = ['*']
        self.valid_prog_environs = ['gromacs']
        
        # created by download_benchmarks():
        self.sourcesdir = os.path.join(self.prefix, 'downloads', 'gromacs', self.casename)

        self.executable = 'gmx_mpi'
        self.executable_opts = ['mdrun', '-s', 'benchmark.tpr', '-g', self.logfile, '-noconfout']
        self.exclusive_access = True
        self.time_limit = None # TODO: set this to something reasonable??
        
        self.keep_files = [self.logfile]
        self.sanity_patterns = sn.assert_found(r'Performance:', self.stderr)
        self.perf_patterns = {
            'ns_per_day': sn.extractsingle(r'Performance:\s+(\S+)\s+(\S+)', self.logfile, 1, float),
            'hour_per_ns':  sn.extractsingle(r'Performance:\s+(\S+)\s+(\S+)', self.logfile, 2, float),
        }
        # TODO: these are basically the same so just keep ns_per_day (higher = better)?
        self.reference = {
            '*': {
                'ns_per_day': (0, None, None, 'ns/day'),
                'hour_per_ns': (0, None, None, 'hour/ns'),
            }
        }

        # example output from logfile:
        # <snip>
        #                Core t (s)   Wall t (s)        (%)
        #        Time:    73493.146     1148.330     6400.0
        #                  (ns/day)    (hour/ns)
        # Performance:        1.505       15.947
        # Finished mdrun on rank 0 Wed Jun  3 17:18:58 2020
        #
        # <EOF>
        
    @rfm.run_before('run')
    def download_benchmarks(self, ):
        """ Download & unpack HECBioSim Gromacs benchmarks
        
            NB: This saves and unpacks it to a persistent location defined by `self.sourcesdir`
                - reframe will then copy it into the staging dir.
        """
        
        benchmark_url = 'http://www.hecbiosim.ac.uk/gromacs-benchmarks/send/2-software/8-gromacs-bench'
        download_dir = os.path.join(self.prefix, 'downloads') # i.e. downloads/ will be alongside this file
        download_dest = os.path.join(download_dir, 'hecbiosim-gromacs.tar.gz')
        download(benchmark_url, download_dest, download_dir)

# TODO: move this into modules
def download(url, download_dest, extract_dir=None):
    """ Download resources with caching.

        Args:
            url: str, url to download from
            download_dest: str, path to download resource at `url` to. This should include the filename
            and also the extension if unpacking is required. If this path exists then `url` will not be downloaded.
            extract_dir: str, path to directory to unpack to, or None if no unpacking is required.
        Directories will be created if required.
        Returns ???
    """

    if not os.path.exists(download_dest):
        download_dir = os.path.dirname(download_dest)
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
        urllib.request.urlretrieve(url, download_dest)
    if extract_dir is not None:
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir, exist_ok=True)
        shutil.unpack_archive(download_dest, extract_dir)
    

def nnodes_param(last=1):
    """ Parameterise the number of nodes for a task.
    
        Starts at max nodes reported by slurm and then halves down to `last` (inclusive).

        Returns a sequence of ints.
    """
    
    nums = []
    n_nodes = len(reframe_extras.slurm_node_info())
    i = 0
    while True:
        n = int(n_nodes/pow(2,i))
        nums.append(n)
        if n <= last:
            return nums
        i += 1

@rfm.parameterized_test(*[[n] for n in nnodes_param()])
class Gromacs_1400k(Gromacs_HECBioSim):
    def __init__(self, num_nodes):
        """ HEC BioSim 1.4M atom Gromacs benchmark.

            Based on https://github.com/hpc-uk/archer-benchmarks/blob/master/apps/GROMACS/1400k-atoms/run/CSD3-Skylake/submit.slurm

            This is parameterised to run on 1 node up to as many nodes are available.
            For each run `n_cores * cpu_factor` x processes are used per node.

            TODO: use openmp?
        """
        
        super().__init__('1400k-atoms')

        cpu_factor = 0.5 # define fraction of cores to use - 0.5 here because alaska has hyperthreading/SMT turned on
        max_cpus = int(reframe_extras.slurm_node_info()[0]['CPUS']) # 0: arbitrarily use first nodes info
        
        self.num_tasks = num_nodes * int(max_cpus * cpu_factor)
        self.num_tasks_per_node = int(self.num_tasks / num_nodes)
                
        self.use_cache = False # set to True to debug outputs using cached results

@rfm.parameterized_test(*[[n] for n in nnodes_param()])
class Gromacs_61k(Gromacs_HECBioSim):
    def __init__(self, num_nodes):
        """ HEC BioSim 61k atom Gromacs benchmark.

            Based on https://github.com/hpc-uk/archer-benchmarks/blob/master/apps/GROMACS/1400k-atoms/run/CSD3-Skylake/submit.slurm

            This is parameterised to run on 1 node up to as many nodes are available.
            For each run `n_cores * cpu_factor` x processes are used per node.

            TODO: use openmp?
        """
        
        super().__init__('61k-atoms')

        cpu_factor = 0.5 # define fraction of cores to use - 0.5 here because alaska has hyperthreading/SMT turned on
        max_cpus = int(reframe_extras.slurm_node_info()[0]['CPUS']) # 0: arbitrarily use first nodes info
        
        self.num_tasks = num_nodes * int(max_cpus * cpu_factor)
        self.num_tasks_per_node = int(self.num_tasks / num_nodes)
                
        self.use_cache = False # set to True to debug outputs using cached results

@rfm.parameterized_test(*[[n] for n in nnodes_param()])
class Gromacs_3000k(Gromacs_HECBioSim):
    def __init__(self, num_nodes):
        """ HEC BioSim 3M atom Gromacs benchmark.

            Based on https://github.com/hpc-uk/archer-benchmarks/blob/master/apps/GROMACS/1400k-atoms/run/CSD3-Skylake/submit.slurm

            This is parameterised to run on 1 node up to as many nodes are available.
            For each run `n_cores * cpu_factor` x processes are used per node.

            TODO: use openmp?
        """
        
        super().__init__('3000k-atoms')

        cpu_factor = 0.5 # define fraction of cores to use - 0.5 here because alaska has hyperthreading/SMT turned on
        max_cpus = int(reframe_extras.slurm_node_info()[0]['CPUS']) # 0: arbitrarily use first nodes info
        
        self.num_tasks = num_nodes * int(max_cpus * cpu_factor)
        self.num_tasks_per_node = int(self.num_tasks / num_nodes)
                
        self.use_cache = False # set to True to debug outputs using cached results
