import fileinput
import pandas as pd
import re

def get_params_from_name(display_name):
    """ Return a dictionary of parameters and their values from the given input string, if present.

        Args:
            display_name: str, expecting a format of <test_name> followed by one or more %<param>=<value> pairs.

    """

    params = display_name.split(" %")

    return dict(zip((p.split("=")[0] for p in params[1:]), (p.split("=")[1] for p in params[1:])))

# a modified and updated version of the function from perf_logs.py
def read_perflog(path):
    """ Return a pandas dataframe from a ReFrame performance log.

        Args:
            path: str, path to log file.

        NB: This currently depends on having a non-default handlers_perflog.filelog.format in reframe's configuration. See code.

        The returned dataframe will have columns for all fields in a performance log record.
    """

    REQUIRED_LOG_FIELDS = ["job_completion_time", r"\w+_value$", r"\w+_unit$"]
    records = []

    with fileinput.input(path) as f:

        try:

            for line in f:

                # split columns
                columns = line.strip().split("|")

                # find all column names
                if fileinput.isfirstline():
                    LOG_FIELDS = columns
                    # look for field names that match required columns
                    required_field_matches = [len([match for match in filter(re.compile(rexpr).match, LOG_FIELDS)]) > 0 for rexpr in REQUIRED_LOG_FIELDS]
                    # check all required columns are present
                    if False in required_field_matches:
                        raise KeyError("Perflog missing one or more required fields", REQUIRED_LOG_FIELDS)
                else:
                    # store as dictionary
                    record = dict(zip(LOG_FIELDS, columns))
                    records.append(record)

        except Exception as e:
            e.args = (e.args[0] + ": during processing %s" % path,) + e.args[1:]
            raise

    return pd.DataFrame.from_records(records)
