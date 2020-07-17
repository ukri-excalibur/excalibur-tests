import os, datetime, fnmatch, subprocess
import pandas as pd
import matplotlib.pyplot as plt

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


def group_by(seq, keyfunc):
    """ group a sequence of nested dicts using a keyfunction
    
        returns a dict of lists
        unlike itertools.groupby this returns a copy not an iterator
    
        TODO: explain properly
    """
    output = {}
    for item in seq:
        value = keyfunc(item)
        curr = output.setdefault(value, [])
        curr.append(item)
    return output

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

def diff_meta(results, ignore=['path']): # TODO: depreciated, replace with diff_dict
    """ Given a sequence of results dicts, returns
            
            common, [difference1, difference2, ...]
        
        where each of these are dicts based on the ['meta'] properties of each result dict,
        ignoring given keys
        
        TODO: describe this properly
    """
    
    meta = [r['meta'].copy() for r in results]
    
    for key in ignore:
        for m in meta:
            m.pop(key, None)
    keyvals = [set(zip(m.keys(), m.values())) for m in meta]
    common = keyvals[0].intersection(*keyvals[1:])
    differences = [dict(sorted(b.difference(common))) for b in keyvals]
    return dict(common), differences

def read_perflog(path):
    """ Return a pandas dataframe from a ReFrame performance log.
    
        Args:
            path: str, path to log file.
        
        NB: This currently depends on having a non-default handlers_perflog.filelog.format in reframe's configuration. See code.

        The returned dataframe will have columns for:
            - qll keys returned by `parse_path_metadata()`
            - all fields in a performance log record, noting that 'completion_time' is converted to a `datetime.datetime`
            - 'perf_var' and 'perf_value', derived from 'perf_info' field
    """
    
    # NB:
    # b/c perflog prefix is '%(check_system)s/%(check_partition)s/%(check_environ)s/%(check_name)s'
    # we know that this is unique for this combo - as it was for results
    records = []
    meta = parse_path_metadata(path)

    with open(path) as f:

        for line in f:
            
            # turn the line into a dict so we can access it:
            line = line.strip()
            # TODO: read this from reframe-settings handlers_perflog.filelog.format? (is adapted tho)
            LOG_FIELDS = 'completion_time,reframe,info,jobid,perf_data,perf_unit,perf_ref'.split(',')
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

            records.append(record)
            
    return pd.DataFrame.from_records(records)

def load_perf_logs(root='.', test=None, ext='.log'):
    """ Convenience wrapper around read_perflog().
    
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
    return perf_records

def sizeof_fmt(num, suffix='B'):
    """ TODO: """
    # from https://stackoverflow.com/a/1094933/916373
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
