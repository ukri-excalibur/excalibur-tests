# moved from utils.py to separate the pandas dependency

import pandas as pd

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
