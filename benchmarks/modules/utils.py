import os
import datetime
import fnmatch
import subprocess
import json
import sys
import pprint

import reframe as rfm
from reframe.core.exceptions import BuildSystemError, CommandLineError
from reframe.core.logging import getlogger
from reframe.utility.osext import run_command
import reframe.utility.osext as osext
import reframe.utility.sanity as sn
SYSFILE = 'systems/sysinfo.json' # interpreted relative to jupyter root

def get_jupyter_root():
    """ Return the path (str) to the root of the jupyter notebook environment, or None """
    jpid = os.getenv('JPY_PARENT_PID')
    if jpid is None:
        return None
    return os.readlink('/proc/%s/cwd' % jpid)

def read_cjson(path):
    """ Read a json file with #-comment lines """
    with open(path) as f:
        lines = [line for line in f if not line.strip().startswith('#')]
    data = json.loads('\n'.join(lines))
    return data

def get_sys_param(param):
    """ Get values of a given parameter from SYSFILE for all systems+partitions.

        Args:
            param: str, parameter within system definition(s) in SYSFILE

        Returns a dict where keys are from SYSFILE, i.e. system:partition patterns and values are the given parameter value.
    """
    results = {}
    jroot = get_jupyter_root() or ''
    syspath = os.path.join(jroot, SYSFILE)
    sysdata = read_cjson(syspath)
    for syspart, params in sysdata.items():
        if param in params:
            results[syspart] = params[param]
    return results


def get_sysinfo(sys_part):
    """ Get system data from SYSFILE for a given system+partition.

        Args:
            sys_part: A full 'system:partion' string

        Returns a dict.
    """
    results = {}
    jroot = get_jupyter_root() or ''
    syspath = os.path.join(jroot, SYSFILE)
    sysdata = read_cjson(syspath)
    for k, v in sysdata.items():
        if fnmatch.fnmatch(sys_part, k):
            results.update(sysdata[k])
    return results

def parse_time_cmd(s):
    """ Convert timing info from `time` into float seconds.
       E.g. parse_time('0m0.000s') -> 0.0
    """

    s = s.strip()
    mins, _, secs = s.partition('m')
    mins = float(mins)
    secs = float(secs.rstrip('s'))

    return mins * 60.0 + secs

def git_describe():
    """ Return a string describing the state of the git repo in which the working directory is.

        See `git describe --dirty --always` for full details.
    """
    cmd = 'git describe --dirty --always'.split()
    proc = subprocess.run(cmd, capture_output=True, universal_newlines=True)
    proc.check_returncode()
    if proc.stderr:
        raise ValueError(proc.stderr)
    return proc.stdout.strip()

def parse_path_metadata(path):
    """ Return a dict of reframe info from a results path """
    parts = path.split(os.path.sep)
    #sysname, partition, environ, testname, filename = parts[-5:]
    COMPONENTS = ('sysname', 'partition', 'environ', 'testname', 'filename')
    info = dict(zip(COMPONENTS, parts[-5:]))
    info['path'] = path
    return info

def find_run_outputs(root='.', test='*', ext='.out'):
    """ Find test files within an output tree.

        Args:
            root: str, path to start searching from
            test: str, limit results to last directory component matching this (can use shell-style wildcards), default any
            ext: str, limit results to files with this extension

        Returns a sequence of str paths.
    """

    # directory is soemthing like:
    # ../output/sausage-newslurm/compute/gnu8-openmpi3/IMB_MPI1Test/

    # TODO: use reframe/reframe/frontend/cli.py code to get the current system, something like
    # import reframe
    # import reframe.core.config as config
    # import reframe.core.runtime as runtime
    # import os

    # # assume default location!
    # print(reframe.INSTALL_PREFIX)
    # config_file = os.path.join(reframe.INSTALL_PREFIX, 'reframe/settings.py')
    # settings = config.load_settings_from_file(config_file)
    # runtime.init_runtime(settings.site_configuration, options.system,
    #                              non_default_craype=options.non_default_craype)

    results = []
    for (dirpath, dirnames, filenames) in os.walk(root):
        # in-place filter dirnames to avoid hidden directories:
        for idx, d in enumerate(dirnames):
            if d.startswith('.'):
                del dirnames[idx]
        for f in filenames:
            if os.path.splitext(f)[-1] == ext:
                path = os.path.join(dirpath, f)
                testdir = os.path.basename(os.path.dirname(path))
                if fnmatch.fnmatchcase(testdir, test):
                    results.append(path)
    return(results)

def diff_dicts(dicts, ignore=None):
    """ Given a sequence of dicts, returns

            common, [difference1, difference2, ...]

        where `commmon` is a dict containing items in all dicts, and `differenceN` is a dict containing keys
        unique to the corresponding dict in `dicts`, ignoring any keys in `ignore`.
    """

    dicts = [d.copy() for d in dicts]
    ignore = [] if ignore is None else ignore
    for key in ignore:
        for d in dicts:
            d.pop(key, None)
    keyvals = [set(zip(d.keys(), d.values())) for d in dicts]
    common = keyvals[0].intersection(*keyvals[1:])
    differences = [dict(sorted(b.difference(common))) for b in keyvals]
    return dict(common), differences

def sizeof_fmt(num, suffix='B'):
    """ TODO: """
    # from https://stackoverflow.com/a/1094933/916373
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

# TODO: put tests in docstrings
# TESTD = {
#     'numbers': {'zero':0, 'one':1},
#     'letters':{'a':'alpha', 'b':'bravo'},
# }

def get_nested(dct, key_pattern):
    """ Get value(s) from a nested dict

        Args:
            dct: dict having str keys and values which may be other `dct`s
            key_pattern: str giving dotted key

        Returns the value. Note that if key_pattern does not go to full depth then a dict is returned.
    """
    d = dct
    patt_parts = key_pattern.split('.')
    for kp in patt_parts:
        if kp in d:
            d = d[kp]
        else:
            raise KeyError("No such key '%s'" % key_pattern)
    return d

# x = get_nested(TESTD, 'letters')
# print(x)

def split_numeric(s):
    """ Split a string into numeric and non-numeric parts """
    num, alpha = [], []
    for c in s:
        if c.isdigit():
            num.append(c)
        else:
            alpha.append(c)
    return ''.join(num), ''.join(alpha)

def singleval(seq, sep=', '):
    """ Convert an object to a single value.

        If the object has no length it is returned as-is.
        If the object is a sequence or set of length 1 the first value is returned.
        If the object is a sequence or set of length > 1 a string concatenation using `sep` is returned.
    """
    if not hasattr(seq, '__len__'):
        return seq
    if len(seq) == 1:
        return list(seq)[0]
    return sep.join(str(v) for v in seq)

def identify_build_environment(current_partition):
    # Select the Spack environment:
    # * if `EXCALIBUR_SPACK_ENV` is set, use that one
    # * if not, use a provided spack environment for the current partition
    # * if that doesn't exist, create a persistent minimal environment
    if os.getenv('EXCALIBUR_SPACK_ENV'):
        env_dir = cp_dir = os.getenv('EXCALIBUR_SPACK_ENV')
        subdir = ''
    else:
        system, partition = current_partition.fullname.split(':')
        cp_dir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), '..', 'spack',
                         system))
        subdir = partition
        env_dir = os.path.join(cp_dir, partition)
        if not os.path.isdir(cp_dir):
            cmd = run_command(["spack", "env", "create", "--without-view", "-d", env_dir])
            if cmd.returncode != 0:
                raise BuildSystemError("Creation of the Spack "
                                       f"environment {env_dir} failed")
            getlogger().info("Spack environment successfully created at"
                             f"{env_dir}")
    return env_dir, cp_dir, subdir


class SpackTest(rfm.RegressionTest):
    build_system = 'Spack'
    spack_spec = variable(str, value='', loggable=True)
    spack_spec_dict = variable(str, value='', loggable=True)
    profiler = variable(str, value='', loggable=True)

    @run_before('compile')
    def setup_spack_environment(self):
        env_dir, cp_dir, subdir = identify_build_environment(
            self.current_partition)
        dest = os.path.join(self.stagedir, 'spack_env')
        self.build_system.environment = os.path.join(dest, subdir)
        # Base name and full path of common settings file.
        spack_envs = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                   '..', 'spack'))
        common_base = 'common.yaml'
        common = os.path.realpath(os.path.join(spack_envs, common_base))
        self.prebuild_cmds = [
            # Copy over the common file.  It should be two levels up compared
            # to the Spack environment, which is the stage directory.
            f'cp {common} {self.stagedir}/{common_base}',
            # Copy over our custom Spack repo.
            f'cp -r {spack_envs}/repo {self.stagedir}/repo',
            # Copy Spack environment (only specific YAML files) to the stage
            # directory.
            f'mkdir -p {dest}',
            f'(cd {cp_dir}; find . \\( -name "spack.yaml" -o -name "compilers.yaml" -o -name "packages.yaml" -o -name "upstreams.yaml" \\) -print0 | xargs -0 tar cf - | tar -C {dest} -xvf -)',
            f'spack -e {self.build_system.environment} config add "config:install_tree:root:{env_dir}/opt"',
        ]
        cmd_spack_spec_dict =   'from spack import environment;\
                                spec_list = environment.active_environment().concrete_roots();\
                                key_list_for_each = [spec.variants.dict.keys() for spec in spec_list];\
                                result_dict = {spec.name: {"compiler": {"name": spec.compiler.name, "version": str(spec.compiler.versions).lstrip("=")}, "variants": {key: str(spec.variants.dict[key].value) if isinstance(spec.variants.dict[key].value, bool) else "" if spec.variants.dict[key].value is None else list(spec.variants.dict[key].value) if isinstance(spec.variants.dict[key].value, tuple) else spec.variants.dict[key].value for key in key_list_for_each[i]},"mpi":str(spec["mpi"]) if "mpi" in spec else ""  } for i, spec in enumerate(spec_list)};\
                                print(result_dict)'
        self.postrun_cmds.append(f'echo "spack_spec_dict: $(spack -e {self.build_system.environment} python -c \'{cmd_spack_spec_dict}\')"')

        # Keep the `spack.lock` file in the output directory so that the Spack
        # environment can be faithfully reproduced later.
        self.keep_files.append(os.path.realpath(os.path.join(self.build_system.environment, 'spack.lock')))


    @run_after('run')
    def get_full_variants(self):
        with osext.change_dir(self.stagedir):
            self.spack_spec_dict = sn.extractsingle(r'spack_spec_dict: \s*(.*)', self.stdout, 1).evaluate()
            # convert all single quotes to double quotes since JSON does not recognise it
            self.spack_spec_dict = self.spack_spec_dict.replace("'", "\"")


    @run_before('compile')
    def setup_build_system(self):
        # The `self.spack_spec` attribute is the user-facing and loggable
        # variable we use for setting the Spack spec, but then we need to
        # forward its value to `self.build_system.specs`, which is the way to
        # inform ReFrame which Spack specs to use.
        self.build_system.specs.append(self.spack_spec)


    @run_before('compile')
    def add_profiler(self):
        if self.profiler:
            # Command to use to view profiling traces
            viewer_cmd = None
            # Arguments to pass to the viewer
            viewer_args = ''
            if self.profiler == 'advisor-roofline':
                pkg_spec = 'intel-oneapi-advisor'
                # Spack package providing the profiler
                self.build_system.specs.append(pkg_spec)
                # Name of output directory
                output_path = 'advisor-roofline'
                # Prepend advisor call to the executable
                self.executable = f'advisor -collect roofline --project-dir={output_path} -- ' + self.executable
                # Save the output directory
                self.keep_files.append(output_path)
                viewer_cmd = 'advisor-gui'
                viewer_args = f'{self.outputdir}/{output_path}'
            elif self.profiler == 'nsight':
                # Spack package providing the profiler
                self.build_system.specs.append('nvidia-nsight-systems')
                # Name of output file
                output_path = 'nsys-trace'
                # Prepend nsys call to the executable
                self.executable = f'nsys profile --trace=cuda,mpi,nvtx,openmp,osrt,opengl,syscall --output {output_path} ' + self.executable
                # Save the output file
                self.keep_files.append(f'{output_path}.nsys-rep')
                viewer_cmd = 'nsys-ui'
                viewer_args = f'{self.outputdir}/{output_path}.nsys-rep'
            elif self.profiler == 'vtune':
                pkg_spec = 'intel-oneapi-vtune'
                # Spack package providing the profiler
                self.build_system.specs.append(pkg_spec)
                # Name of output directory
                output_path = 'vtune-profiling'
                # Prepend VTune call to the executable
                self.executable = f'vtune -collect hotspots -r {output_path} -- ' + self.executable
                # Save the output directory
                self.keep_files.append(f'{output_path}*')
                viewer_cmd = 'vtune-gui'
                viewer_args = f'{self.outputdir}/{output_path}*'
            else:
                raise CommandLineError(f'Unknown profiler {self.profiler}')

            # Hack time! On ARCHER2 the home partition isn't mounted on compute
            # nodes, but due to a longstanding upstream bug
            # (<https://community.intel.com/t5/Intel-MPI-Library/How-to-install-beta8-without-it-getting-near-home-directory/m-p/1211465>),
            # Intel tools want to *write* into the home directory at any cost.
            # We trick them by setting the HOME env var to their installation
            # directory.  Note: we use `prerun_cmds` instead of `env_vars` so
            # that we do this only right before running the benchmark command
            # and not also before compilation, where `spack location` wouldn't
            # even work.  Let's hope nothing else relies on HOME being set to
            # the actual home directory (also because it isn't accessible, you
            # know).
            if self.profiler in ('advisor-roofline', 'vtune') and self.current_system.name == 'archer2':
                self.prerun_cmds.append(f'export HOME=$(spack -e {self.build_system.environment} location --install-dir {pkg_spec})')

            if viewer_cmd:
                # Print to stdout the command to use for viewing the profiling
                # results.
                self.postrun_cmds.append(f'''
if which {viewer_cmd} 2> /dev/null; then
    echo "You can view the profiler output with the command"
    echo "    $(which {viewer_cmd}) {viewer_args}"
fi''')


    @run_before('compile')
    def set_sge_num_slots(self):
        if self.current_partition.scheduler.registered_name == 'sge':
            # `self.num_tasks` or `self.num_cpus_per_task` may be `None`, here
            # we default to `1` if not set.
            num_tasks = self.num_tasks or 1
            num_cpus_per_task = self.num_cpus_per_task or 1
            # Set the total number of CPUs to be requested for the SGE scheduler.
            if self.current_system.name == 'kathleen':
                self.extra_resources['mpi'] = {'num_slots': max(41, num_tasks * num_cpus_per_task)}
            else:
                self.extra_resources['mpi'] = {'num_slots': num_tasks * num_cpus_per_task}

    @run_before('compile')
    def set_isambard_memory(self):
        # We define the `memory` extra resource, so that we
        # can use the corresponding resources in the config file.
        system, partition = self.current_partition.fullname.split(':')
        if system == "isambard-phase3":
            self.extra_resources['memory'] = {}

    @run_after('setup')
    def setup_build_job_num_cpus(self):
        # When running a build on a compute node, ReFrame by default uses only a
        # single CPU, which is a large waste of time and resources.  With this,
        # we force the build job to always use 16 CPUs or all available CPUs on
        # the target partition, whichever is smaller, because on some systems
        # using full partitions may have lower priority.
        if not self.build_locally:
            self.build_job.num_cpus_per_task = min(16, self.current_partition.processor.num_cpus)



if __name__ == '__main__':

    #v = get_sysinfo(sys.argv[-1])
    v = get_sys_param(sys.argv[-1])
    pprint.pprint(v)
