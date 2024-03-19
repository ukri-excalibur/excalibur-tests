import reframe as rfm
import reframe.utility.sanity as sn
import sys, os, urllib
sys.path.append('.')
from modules.reframe_extras import scaling_config 
from modules.utils import parse_time_cmd

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
    def __init__(self, benchmark, part, num_tasks, num_tasks_per_node):

        self.benchmark = benchmark
        self.num_tasks = num_tasks
        self.num_tasks_per_node = num_tasks_per_node
        self.num_nodes = int(self.num_tasks / self.num_tasks_per_node)

        self.valid_systems = [part]
        self.valid_prog_environs = ['castep']

        self.sourcesdir = 'downloads' # will actually copy all benchmark .tgz files to stage dir
        self.prerun_cmds = [
            'tar --strip-components=%i -xf %s.tgz' % (BENCHMARKS[self.benchmark]['strip_dirs'], self.benchmark),
            'time \\']
        self.executable = 'castep'
        
        self.seedname = BENCHMARKS[self.benchmark]['seedname']
        self.executable_opts = [self.seedname]
        
        self.exclusive_access = True
        
        self.tags |= {self.benchmark, 'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes}
        self.logfile = '%s.castep' % self.seedname
        self.keep_files = [self.logfile]
        
        self.sanity_patterns = sn.all([
            sn.assert_found(r'Total time', self.logfile),
        ])
        self.perf_patterns = {
            # from castep output:
            'total_time': sn.extractsingle(r'Total time\s+=\s+([\d.]+) s', self.logfile, 1, float),
            'peak_mem': sn.extractsingle(r'Peak Memory Use\s+=\s+([\d.]+) kB', self.logfile, 1, float),
            'parallel_efficiency': sn.extractsingle(r'Overall parallel efficiency rating: \S+ \((\d+)%\)', self.logfile, 1, float),
            # from `time`:
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
        }
        self.reference = {
            '*': {
                'total_time': (0, None, None, 's'),
                'peak_mem': (0, None, None, 'kB'),
                'parallel_efficiency': (0, None, None, '%'),
                'runtime_real': (0, None, None, 's'),
            }
        }
    
    @rfm.run_after('setup')
    def download_benchmark(self):
        """ Download benchmark to the tests benchmark/ directory - NB this must exist. """
        download_path = os.path.join(self.prefix, 'downloads', '%s.tgz' % self.benchmark)
        if not os.path.exists(download_path):
            urllib.request.urlretrieve(BENCHMARKS[self.benchmark]['url'], download_path)


@rfm.parameterized_test(*scaling_config())
class Castep_Al3x3(Castep_Base):
    """ Medium benchmark Al3x3: http://www.castep.org/CASTEP/Al3x3 """
    def __init__(self, part, num_tasks, num_tasks_per_node):
        
        super().__init__('Al3x3', part, num_tasks, num_tasks_per_node)
        self.time_limit = '2h'

@rfm.simple_test
class Castep_TiN(Castep_Base):
    """ Small benchmark TiN: http://www.castep.org/CASTEP/TiN
    
        Not expected to scale well past 8x processes.
    """
    
    def __init__(self):

        super().__init__('TiN', '*', 8, 8)
        self.time_limit = '1h'


@rfm.parameterized_test(*scaling_config())
class Castep_DNA(Castep_Base):
    """ Large benchmark DNA: http://www.castep.org/CASTEP/DNA """
    def __init__(self, part, num_tasks, num_tasks_per_node):
        
        super().__init__('DNA', part, num_tasks, num_tasks_per_node)
        self.time_limit = '1d' # TODO: adjust?
