import reframe as rfm
import reframe.utility.sanity as sn
import sys, os, urllib
sys.path.append('.')
from modules.reframe_extras import ScalingTest 
from modules.utils import parse_time_cmd

NODE_STEPS = [-1, -2, 0.25, 0.5, 1.0] # -ve numbers are absolute numbers of nodes, +ve are fraction of total partition nodes

BENCHMARKS = {
    'Al3x3': {
        'url': "http://www.castep.org/CASTEP/Al3x3?action=download&upname=al3x3.tgz",
        'strip_dirs': 2, # number of levels inside .tgz before the actual files
        'seedname': 'al3x3' # *.param and *.cell name, not always same as benchmark name
    },
    'DNA': {
        'url': "http://www.castep.org/CASTEP/DNA?action=download&upname=DNA.tgz",
        'strip_dirs': 1,
        'seedname': 'polyA20-no-wat'
    },
    'TiN': {
        'url': "http://www.castep.org/CASTEP/TiN?action=download&upname=TiN.tgz",
        'strip_dirs': 1,
        'seedname': 'TiN-mp'
        }
    }


class Castep_Base(rfm.RunOnlyRegressionTest):
    """ Base class for Castep - downloads benchmark to ./downloads/ and unpacks .tgz to stage dir.
    
        Requires child classes to set:
        - `self.benchmark': key from BENCHMARKS
    """
    # TODO: calculate scf cycles/hour or /sec
    def __init__(self):

        self.valid_systems = ['*']
        self.valid_prog_environs = ['castep']

        self.sourcesdir = 'downloads' # will actually copy all benchmark .tgz files to stage dir
        self.prerun_cmds = [
            'tar --strip-components=%i -xf %s.tgz' % (BENCHMARKS[self.benchmark]['strip_dirs'], self.benchmark),
            'time \\']
        self.executable = 'castep'
        
        self.seedname = BENCHMARKS[self.benchmark]['seedname']
        self.executable_opts = [self.seedname]
        
        self.exclusive_access = True
        
        self.tags = {self.benchmark}

        self.logfile = '%s.castep' % self.seedname
        self.keep_files = [self.logfile]
        
        self.sanity_patterns = sn.all([
            sn.assert_found(r'Total time', self.logfile),
        ])
        self.perf_patterns = {
            # from castep output:
            'total_time': sn.extractsingle(r'Total time\s+=\s+([\d.]+) s', self.logfile, 1, float),
            'peak_mem': sn.extractsingle(r'Peak Memory Use\s+=\s+([\d.]+) kB', self.logfile, 1, float),
            'parallel_efficienty': sn.extractsingle(r'Overall parallel efficiency rating: \S+ \((\d+)%\)', self.logfile, 1, float),
            # from `time`:
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
        }
        self.reference = {
            '*': {
                'total_time': (0, None, None, 's'),
                'peak_mem': (0, None, None, 'kB'),
                'parallel_efficienty': (0, None, None, '%'),
                'runtime_real': (0, None, None, 's'),
            }
        }
    
    @rfm.run_after('setup')
    def download_benchmark(self):
        """ Download benchmark to the tests benchmark/ directory - NB this must exist. """
        download_path = os.path.join(self.prefix, 'downloads', '%s.tgz' % self.benchmark)
        if not os.path.exists(download_path):
            urllib.request.urlretrieve(BENCHMARKS[self.benchmark]['url'], download_path)


@rfm.parameterized_test(*[[n] for n in NODE_STEPS])
class Castep_Al3x3(Castep_Base, ScalingTest):
    """ TODO: """
    def __init__(self, num_nodes):
        self.benchmark = 'Al3x3'
        self.partition_fraction = num_nodes
        self.node_fraction = 1 # use all cores
        self.time_limit = '1h' # TODO: is this enough?
        super().__init__()


@rfm.simple_test
class Castep_TiN(Castep_Base, ScalingTest):
    """ Small TiN test, essentially to check castep works.
    
        See http://www.castep.org/CASTEP/TiN
    """
    
    def __init__(self):

        self.benchmark = 'TiN'
        self.partition_fraction = -1 # node
        self.node_fraction = -8 # 8 processes, apparently the max this really scales to
        self.time_limit = '1h'
        super().__init__()