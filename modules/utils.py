import os, datetime

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

def find_run_outputs(root='.', test=None, ext='.out'):
    """ Find test files within an output tree.
    
        Args:
            root: path to start searching from
            test: str, limit results to test directories (i.e the last part before the filename) which contain this string (default: all)
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
                if test is None or test in testdir:
                    results.append(path)
    return(results)

def diff_meta(results, ignore=['path']):
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
    """ TODO: explain """
    
    # NB:
    # b/c perflog prefix is '%(check_system)s/%(check_partition)s/%(check_environ)s/%(check_name)s'
    # we know that this is unique for this combo - as it was for results
    
    perf_results = {'meta': parse_path_metadata(path)}
    
    with open(path) as f:
        for line in f:
            # turn the line into a dict so we can access it:
            line = line.strip()
            # TODO: read this from reframe-settings handlers_perflog.filelog.format? (is adapted tho)
            LOG_FIELDS = 'completion_time,reframe,info,jobid,perf_data,perf_unit,perf_ref'.split(',')
            record = dict(zip(LOG_FIELDS, line.split('|')))
            
            # process values:
            perf_var, perf_value = record['perf_data'].split('=')
            record['perf_value'] = float(perf_value) # TODO: is this always right?
            record['completion_time'] = datetime.datetime.fromisoformat(record['completion_time'])
            
            # make sure we have a dict of lists for this perf_var:
            # NB unit and ref shouldn't change but best place to store them
            result_fields = ('completion_time', 'jobid', 'perf_value', 'perf_unit', 'perf_ref', 'reframe')
            var_results = perf_results.setdefault(perf_var, {})
            
            # append fields from this record:
            for k in result_fields:
                var_results.setdefault(k, list()).append(record[k])
    
    return perf_results


def sizeof_fmt(num, suffix='B'):
    """ TODO: """
    # from https://stackoverflow.com/a/1094933/916373
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)