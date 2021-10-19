""" Extra functionality for reframe

"""

import reframe as rfm
from reframe.core.buildsystems import BuildSystem
from reframe.core.logging import getlogger
from reframe.core.launchers import JobLauncher
from reframe.core.runtime import runtime
import reframe.utility.sanity as sn

import os, shutil, subprocess, shlex, subprocess
from subprocess import PIPE
from pprint import pprint

def scaling_config(min_nodes=1, max_node_factor=1.0, core_factor=1.0):
    """ Parameterise a test using Slurm over a varying number of nodes.

        Intended to be used as an input to an `@rfm.parameterized_test` e.g. as follows:

            @rfm.parameterized_test(*scaling_config())
            def mytest(rfm.RunOnlyRegressionTest):
                def __init__(self, part, n_tasks, n_tasks_per_node):
                    self.num_tasks = num_tasks
                    self.num_tasks_per_node = num_tasks_per_node
                    self.valid_systems = [part]
        
        Tests will be generated for 1, 2, 4, 8, ..., nodes up to the maximum number of nodes in the appropriate Slurm partition.
        This maximum number is included whether or not it is a power of 2. Any `--partition` or `--exclude` directives in the ReFrame
        partition's `access` property are taken into account.

        For ReFrame partitions which do not use slurm, no test is generated.
        
        Args:
            `min_nodes`: number of nodes to start at (default: 1)
            `max_node_factor`: factor on number of nodes in slurm partition* to use for largest test (default: 1.0)
            `core_factor`: factor on number of physical cores in each node to use for each test (default: 1.0)

        *: or part of it defined by `access` parameters.

        Yields a sequence of (rfm_part_name, n_tasks, n_tasks_per_node) tuples which should be passed to the test's constructor and set as test
        properties as shown in the example above.

        **NB:** It is important that the test using this sets `self.valid_systems` as shown above, else tests may be defined for incorrect partitions.
    """

    curr_sys = runtime().system
    for part in curr_sys.partitions:
        if part.scheduler.registered_name not in ['slurm', 'squeue']:
            continue # ignore non Slurm schedulers

        sched_partition = Scheduler_Info(part)
        n_tasks_per_node = int(sched_partition.pcores_per_node * core_factor)
        
        n = 1
        while n < int(sched_partition.num_nodes * max_node_factor):
            n_tasks = n_tasks_per_node * n
            yield (part.fullname, n_tasks, n_tasks_per_node)
            n *= 2
        # create largest test:
        n_tasks = n_tasks_per_node * int(sched_partition.num_nodes * max_node_factor)
        yield (part.fullname, n_tasks, n_tasks_per_node)

def scaling_config_mock():
    """
    A mock of scaling config that can be used on one's laptop,
    for testing/debugging purposes.
    """
    yield("no-partition",2,2)

class ScalingTest(rfm.RegressionTest):
    """ Mixin to specify the number of nodes and processes-per-node to use relative to current partition resources.

        Classes deriving from this must set the following to a number:

        - `self.partition_fraction`
        - `self.node_fraction`

        If +ve, these give a factor which defines respectively:
        - The number of nodes to use, as the number of nodes in the current scheduler partition * this factor
        - The number of processes to use per node, as the number of physical cores * this factor
        
        If -ve, they must be an integer in which case they define the absolute number of nodes or processes to use respectively.
        
        Note that the current scheduler partition is affected by the (reframe) partition's `access` property. The following `sbatch` directives are
        taken into account:
        - `--partition`: use a non-default Slurm partition.
        - `--exclude`: exclude specific nodes from consideration, i.e. a `partition_fraction` of 1.0 will not use these nodes.

        The following tags are set:
        - `num_nodes`: the number of nodes used.
        - `num_procs`: the total number of MPI tasks used.
        - `procs_per_node`: the number of MPI tasks/processes per node
    """

    @rfm.run_after('setup')
    def set_nodes(self):
        
        scheduler_partition = Scheduler_Info(self.current_partition)

        # calculate number of nodes to use:
        if not hasattr(self, 'partition_fraction'):
            raise NameError('test classes derived from %r must define self.partition_fraction' % type(self))
        if self.partition_fraction < 0:
            if not isinstance(self.partition_fraction, int):
                raise TypeError('invalid self.partition_fraction of %r : -ve values should specify an integer number of nodes' % self.test_size)
            self.num_nodes = -1 * self.partition_fraction
        else:
            self.num_nodes = int(scheduler_partition.num_nodes * self.partition_fraction)
        
        # calculate number of tasks per node:
        if not hasattr(self, 'node_fraction'):
            raise NameError('test classes derived from %r must define self.node_fraction' % type(self))
        if self.node_fraction < 0:
            if not isinstance(self.node_fraction, int):
                raise TypeError('invalid self.node_fraction of %r : -ve values should specify an integer number of cores' % self.test_size)
            self.num_tasks_per_node = -1 * self.node_fraction # reframe parameter
        else:
            self.num_tasks_per_node = int(scheduler_partition.pcores_per_node * self.node_fraction) # reframe parameter
        
        self.num_tasks = self.num_nodes * self.num_tasks_per_node # reframe parameter

        # set tags:
        self.tags |= {'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes, 'procs_per_node=%i' % self.num_tasks_per_node}

class CachedRunTest(rfm.RegressionTest):
    """ Mixin. TODO: document properly.

        Classes using this can be derive from `rfm.RunOnlyRegressionTest`
        Assumes saved output files are in a directory `cache/` in same parent directory (and with same directory tree) as the `output/` and `stage/` directories.

        set self.use_cache to True or a path relative to cwd.
    
        NB Any class using this MUST NOT change self.executable in a method decorated with `@rfm.run_before('run')` as that will override functionality here.
    """

    @rfm.run_before('run')
    def no_run(self):
        """ Turn the run phase into a no-op. """

        if self.use_cache:
            with open(os.path.join(self.stagedir, 'noop.sh'), 'w') as noop:
                noop.write('#!/bin/bash\necho "noop $@"\n')
            self.executable = "./noop.sh"

    @rfm.run_after('run')
    def copy_saved_output(self):
        """ Copy saved output files to stage dir. """

        if self.use_cache:
            # find the part of the path common to both output and staging:
            rtc = rfm.core.runtime.runtime()
            tree_path = os.path.relpath(self.outputdir, rtc.output_prefix)
            
            cache_root = 'cache' if self.use_cache == True else self.use_cache

            saved_output_dir = os.path.join(cache_root, tree_path)
            
            if not os.path.exists(saved_output_dir) or not os.path.isdir(saved_output_dir):
                raise ValueError("cached output directory %s does not exist or isn't a directory" % os.path.abspath(saved_output_dir))

            import distutils.dir_util
            distutils.dir_util.copy_tree(saved_output_dir, self.stagedir)


class CachedCompileOnlyTest(rfm.CompileOnlyRegressionTest):
    """ A compile-only test with caching of binaries between `reframe` runs.
    
        Test classes derived from this class will save `self.executable` to a ./builds/{system}/{partition}/{environment}/{self.name}` directory after compilation.
        However if this path (including the filename) exists before compilation (i.e. on the next run):
            - No compilation occurs
            - `self.sourcesdir` is set to this directory, so `reframe` will copy the binary to the staging dir (as if compilation had occured)
            - A new attribute `self.build_path` is set to this path (otherwise None)

        Note that `self.sourcesdir` is only manipulated if no compilation occurs, so compilation test-cases which modify this to specify the source directory should be fine.

        TODO: Make logging tidier - currently produces info-level (stdout by default) messaging on whether cache is used.
    """
    @rfm.run_before('compile')
    def conditional_compile(self):
        build_dir = os.path.abspath(os.path.join('builds', self.current_system.name, self.current_partition.name, self.current_environ.name, self.name))
        build_path = os.path.join(build_dir, self.executable)
        if os.path.exists(build_path):
            self.build_path = build_path
            getlogger().info('found exe at %r', self.build_path)
            self.build_system = NoBuild()
            self.sourcesdir = build_dir # means reframe will copy the exe back in
        else:
            self.build_path = None

    @rfm.run_after('compile')
    def copy_executable(self):
        if not self.build_path: # i.e. only if actually did a compile:
            self.exes_dir = os.path.join('builds', self.current_system.name, self.current_partition.name, self.current_environ.name, self.name)
            exe_path = os.path.join(self.stagedir, self.executable)
            build_path = os.path.join(self.exes_dir, self.executable)
            build_dir = os.path.dirpath(build_path) # self.executable might include a directory
            if not os.path.exists(build_dir):
                os.makedirs(build_dir)
            shutil.copy(exe_path, build_path)
            getlogger().info('copied exe to %r', build_path)

class NoBuild(BuildSystem):
    """ A no-op build system """
    def __init__(self):
        super().__init__()
    def emit_build_commands(self, environ):
        return []

def slurm_node_info(partition=None):
    """ Get information about slurm nodes.

        Args:
            partition: str, name of slurm partition to query, else information for all partitions is returned.

        Returns a sequence of dicts, one per node with keys/values all strs as follows:
            "NODELIST": name of node
            "NODES": number of nodes
            "PARTITION": name of partition, * appended if default
            "STATE": e.g. "idle"
            "CPUS": str number of cpus
            "S:C:T": Extended processor information: number of sockets, cores, threads in format "S:C:T"
            "MEMORY": Size of memory in megabytes
            "TMP_DISK": Size of temporary disk space in megabytes
            "WEIGHT": Scheduling weight of the node
            "AVAIL_FE": ?
            "REASON": The reason a node is unavailable (down, drained, or draining states) or "none"
        See `man sinfo` for `sinfo --Node --long` for full details.

        TODO: add partition selection? with None being current one (note system partition != slurm partition)
    """
    sinfo_cmd = ['sinfo', '--Node', '--long']
    if partition:
        sinfo_cmd.append('--partition=%s' % partition)
    nodeinfo = subprocess.run(sinfo_cmd, stdout=PIPE, stderr=PIPE).stdout.decode('utf-8') # encoding?

    nodes = []
    lines = nodeinfo.split('\n')
    header = lines[1].split() # line[0] is date/time
    for line in lines[2:]:
        line = line.split()
        if not line:
            continue
        nodes.append({})
        for ci, key in enumerate(header):
            nodes[-1][key] = line[ci]
    return nodes


def hostlist_to_hostnames(s):
    """ Convert a Slurm 'hostlist expression' to a list of individual node names.
    
        Uses `scontrol` command.
    """
    hostnames = subprocess.run(['scontrol', 'show', 'hostnames', s], capture_output=True, text=True).stdout.split()
    return hostnames

class Scheduler_Info(object):
    def __init__(self, rfm_partition=None, exclude_states=None, only_states=None):
        """ Information from the scheduler.

            Args:
                rfm_partition: reframe.core.systems.SystemPartition or None
                exclude_states: sequence of str, exclude nodes in these Slurm node states
                only_states: sequence of str, only include nodes in these Slurm node states
            
            The returned object has attributes:
                - `num_nodes`: number of nodes
                - `sockets_per_node`: number of sockets per node
                - `pcores_per_node`: number of physical cores per node
                - `lcores_per_node`: number of logical cores per node
            
            If `rfm_partition` is None the above attributes describe the **default** scheduler partition. Otherwise the following `sbatch` directives
            in the `access` property of the ReFrame partition will affect the information returned:
                - `--partition`
                - `--exclude`
        """

        # TODO: handle scheduler not being slurm!
        slurm_partition_name = None
        slurm_excluded_nodes = []
        exclude_states = [] if exclude_states is None else exclude_states
        only_states = [] if only_states is None else only_states
        if rfm_partition is not None:
            for option in rfm_partition.access:
                if '--partition=' in option:
                    _, slurm_partition_name = option.split('=')
                if '--exclude' in option:
                    _, exclude_hostlist = option.split('=')
                    slurm_excluded_nodes = hostlist_to_hostnames(exclude_hostlist)
        
        # filter out nodes we don't want:
        nodeinfo = []
        for node in slurm_node_info(slurm_partition_name):
            if slurm_partition_name is None and not node['PARTITION'].endswith('*'): # filter to default partition
                continue
            if node['NODELIST'] in slurm_excluded_nodes:
                continue
            if node['STATE'].strip('*') in exclude_states:
                continue
            if only_states and node['STATE'] not in only_states:
                continue
            nodeinfo.append(node)
            
        self.num_nodes = len(nodeinfo)
        cpus = [n['S:C:T'] for n in nodeinfo]
        if not len(set(cpus)) == 1:
            raise ValueError('Cannot summarise CPUs - description differs between nodes:\n%r' % cpus)
        sockets, cores, threads = [int(v) for v in cpus[0].split(':')] # nb each is 'per' the preceeding
        self.sockets_per_node = sockets
        self.pcores_per_node = sockets * cores
        self.lcores_per_node = sockets * cores * threads

    def __str__(self):

        descr = ['%s=%s' % (k, getattr(self, k)) for k in ['num_nodes', 'sockets_per_node', 'pcores_per_node', 'lcores_per_node']]

        return 'Scheduler_Info(%s)' % (', '.join(descr))

def sequence(start, end, factor):
    """ Like `range()` but each term is `factor` * previous term.

        `start` is inclusive, `end` is exclusive.

        Returns a list.
    """

    values = []
    v = start
    while v < end:
        values.append(v)
        v *= factor
    return values

if __name__ == '__main__':
    import sys
    # will need something like:
    # [hpc-tests]$ PYTHONPATH='reframe' python modules/reframe_extras.py
    if len(sys.argv) == 1:
        print(Scheduler_Info())
    else:
        print(Scheduler_Info(sys.argv[1]))
