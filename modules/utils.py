import os, datetime, fnmatch, subprocess, json, sys, pprint, fnmatch
import pandas as pd
import matplotlib.pyplot as plt


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

def read_perflog(path):
    """ Return a pandas dataframe from a ReFrame performance log.
    
        Args:
            path: str, path to log file.
        
        NB: This currently depends on having a non-default handlers_perflog.filelog.format in reframe's configuration. See code.

        The returned dataframe will have columns for:
            - all keys returned by `parse_path_metadata()`
            - all fields in a performance log record, noting that:
              - 'completion_time' is converted to a `datetime.datetime`
              - 'tags' is split on commas into a list of strs
            - 'perf_var' and 'perf_value', derived from 'perf_info' field
            - <key> for any tags of the format "<key>=<value>", with values converted to int or float if possible
    """
    
    # NB:
    # b/c perflog prefix is '%(check_system)s/%(check_partition)s/%(check_environ)s/%(check_name)s'
    # we know that this is unique for this combo - as it was for results
    records = []
    meta = parse_path_metadata(path)

    with open(path) as f:

        try:

            for line in f:
                
                # turn the line into a dict so we can access it:
                line = line.strip()
                # TODO: read this from reframe-settings handlers_perflog.filelog.format? (is adapted tho)
                LOG_FIELDS = 'completion_time,reframe,info,jobid,perf_data,perf_unit,perf_ref,tags'.split(',')
                record = meta.copy()
                fields = dict(zip(LOG_FIELDS, line.split('|')))
                record.update(fields) # allows this to override metadata
                
                # process values:
                perf_var, perf_value = record['perf_data'].split('=')
                record['perf_var'] = perf_var
                try:
                    record['perf_value'] = float(perf_value)
                except ValueError:
                    record['perf_value'] = perf_value
                record['completion_time'] = datetime.datetime.fromisoformat(record['completion_time'])
                record['jobid'] = record['jobid'].split('=')[-1] # original: "jobid=2378"
                non_kv_tags = []
                tags = record['tags'].split(',')
                for tag in tags:
                    if '=' in tag:
                        k, v = tag.split('=')
                        for conv in (int, float):
                            try:
                                v = conv(v)
                            except ValueError:
                                pass
                            else:
                                break
                        record[k] = v
                record['tags'] = tags
                records.append(record)
        except Exception as e:
            e.args = (e.args[0] + ': during processing %s' % path,) + e.args[1:]
            raise
            
    return pd.DataFrame.from_records(records)

def load_perf_logs(root='.', test=None, ext='.log', last=False):
    """ Convenience wrapper around read_perflog().

        Args:
            root: str, path to root of tree containing perf logs
            test: str, shell-style glob pattern matched against last directory component to restrict loaded logs, or None to load all in tree
            ext: str, only load logs from files with this extension
            last: bool, True to only return the most-recent record for each system/partition/enviroment/testname/perf_var combination.

        Returns a single pandas.dataframe concatenated from all loaded logs, or None if no logs exist.
    """
    perf_logs = find_run_outputs(root, test, ext)
    perf_records = []
    for path in perf_logs:
        records = read_perflog(path)
        perf_records.append(records)
    if len(perf_records) == 0:
        return None
    perf_records = pd.concat(perf_records).reset_index(drop=True)

    if last:
        perf_records = perf_records.sort_index().groupby(['sysname', 'partition', 'environ', 'testname', 'perf_var']).tail(1)
    
    return perf_records

def tabulate_last_perf(test, index, perf_var, root='../../perflogs'):
    """ Retrieve last perf_log entry for each system/partition/environment.

        Args:
            test: str, shell-style glob pattern matched against last directory component to restrict loaded logs, or None to load all in tree
            index: str, name of perf_log parameter to use as index (see `read_perflog()` for valid names)
            perf_var: str, name of perf_var to extract
            root: str, path to root of tree containing perf logs of interest - default assumes this is called from an `apps/<application>/` directory
        
        Returns a dataframe with columns:
            case: TODO:

    """
    
    df = load_perf_logs(root=root, test=test, ext='.log', last=True)
    if df is None: # no data
        return None
    
    # filter to rows for correct perf_var:
    df = df.loc[df['perf_var'] == perf_var]
    
    # keep only the LAST record in each system/partition/environment/xvar
    df = df.sort_index().groupby(['sysname', 'partition', 'environ', index]).tail(1)
    
    # Add "case" column from combined system/partition:
    df['case'] = df[['sysname', 'partition']].agg(':'.join, axis=1)
    
    # reshape to wide table:
    df = df.pivot(index=index, columns='case', values='perf_value')
    
    return df

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


if __name__ == '__main__':
    
    #v = get_sysinfo(sys.argv[-1])
    v = get_sys_param(sys.argv[-1])
    pprint.pprint(v)
    