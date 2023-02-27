import os
import datetime
import fnmatch
import subprocess
import json
import sys
import pprint

import reframe as rfm
from reframe.core.exceptions import BuildSystemError
from reframe.core.logging import getlogger
from reframe.utility.osext import run_command


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
            os.path.join(os.path.dirname(__file__), '..', 'spack-environments',
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

    @run_before('compile')
    def setup_spack_environment(self):
        env_dir, cp_dir, subdir = identify_build_environment(
            self.current_partition)
        dest = os.path.join(self.stagedir, 'spack_env')
        self.build_system.environment = os.path.join(dest, subdir)
        # Base name and full path of common settings file.
        common_base = 'common.yaml'
        common = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                               '..', 'spack-environments', common_base))
        self.prebuild_cmds = [
            # Copy over the common file.  It should be two levels up compared
            # to the Spack environment, which is the stage directory.
            f'cp {common} {self.stagedir}/{common_base}',
            # Copy Spack environment (only specific YAML files) to the stage
            # directory.
            f'mkdir -p {dest}',
            f'(cd {cp_dir}; find . \( -name "spack.yaml" -o -name "compilers.yaml" -o -name "packages.yaml" \) -print0 | xargs -0 tar cf - | tar -C {dest} -xvf -)',
            f'spack -e {self.build_system.environment} config add "config:install_tree:root:{env_dir}/opt/spack"',
        ]


if __name__ == '__main__':

    #v = get_sysinfo(sys.argv[-1])
    v = get_sys_param(sys.argv[-1])
    pprint.pprint(v)
