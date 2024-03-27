import errno
import json
import os
import re
from itertools import chain

import pandas as pd


class PerflogHandler:

    def __init__(self, log_path, debug=False):

        self.log_path = log_path
        self.debug = debug

        self.get_log_files()
        self.read_all_perflogs()

    def get_df(self):
        return self.df

    def get_log_files(self):
        """
            Search for all performance logs in class log path. Record found logs in class
            log file list.
        """

        self.log_files = []
        # one perflog supplied
        if os.path.isfile(self.log_path):
            # check correct log extension
            if os.path.splitext(self.log_path)[1] != ".log":
                raise RuntimeError("Perflog file name provided should have a .log extension.")
            self.log_files = [self.log_path]

        # look for perflogs in folder
        elif os.path.isdir(self.log_path):
            for file in [os.path.join(root, file) for root, _, files
                         in os.walk(self.log_path) for file in files]:
                # append files with correct log extension
                if os.path.splitext(file)[1] == ".log":
                    self.log_files.append(file)
            # no perflogs in folder
            if len(self.log_files) == 0:
                raise RuntimeError(
                    "No perflogs found in this path. Perflogs should have a .log extension.")

        # invalid path
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.log_path)

        if self.debug:
            print("Found log files:")
            for log in self.log_files:
                print("-", log)
            print("")

    def read_all_perflogs(self):
        """
            Return a pandas dataframe containing information from all reframe performance logs
            in class log file list.
        """

        self.df = pd.DataFrame()
        # put all perflog information in one dataframe
        for file in self.log_files:
            try:
                self.df = pd.concat([self.df, read_perflog(file)], ignore_index=True)
            # discard invalid perflogs
            except KeyError as e:
                if self.debug:
                    print("Discarding %s:" % os.path.basename(file),
                          type(e).__name__ + ":", e.args[0], e.args[1])
                    print("")

        # no valid perflogs found
        if self.df.empty:
            raise FileNotFoundError(
                errno.ENOENT, "Could not find a valid perflog in path", self.log_path)


def read_perflog(path):
    """
        Return a pandas dataframe from a reframe performance log. The dataframe will
        have columns for all fields in a performance log record except display name,
        extra resources, and env vars. Display name will be broken up into test name and
        parameter columns, while the other two will be replaced by the dictionary contents
        of their fields (keys become columns, values become row contents).

        NB: This currently depends on having a non-default handlers_perflog.filelog.format
            in reframe's configuration. See code.

        Args:
            path: path, path to log file.
    """

    # read perflog into dataframe
    df = pd.read_csv(path, delimiter="|")
    REQUIRED_LOG_FIELDS = ["job_completion_time", r"\w+_value$", r"\w+_unit$", "display_name"]

    # look for required column matches
    required_field_matches = [len(list(filter(re.compile(rexpr).match, df.columns))) > 0
                              for rexpr in REQUIRED_LOG_FIELDS]
    # check all required columns are present
    if False in required_field_matches:
        raise KeyError("Perflog missing one or more required fields", REQUIRED_LOG_FIELDS)

    # replace display name
    results = df["display_name"].apply(get_display_name_info)
    index = df.columns.get_loc("display_name")
    # insert new columns and contents
    insert_key_cols(df, index, [r[1] for r in results])
    df.insert(index, "test_name", [r[0] for r in results])
    # drop old column
    df.drop("display_name", axis=1, inplace=True)

    # replace other columns with dictionary contents
    dict_cols = [c for c in ["extra_resources", "env_vars", "spack_spec_dict"] if c in df.columns]
    for col in dict_cols:
        results = df[col].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        # insert new columns and contents
        insert_key_cols(df, df.columns.get_loc(col), results)
        # drop old column
        df.drop(col, axis=1, inplace=True)

    return df


def get_display_name_info(display_name):
    """
        Return a tuple containing the test name and a dictionary of parameter names
        and their values from the given input string. The parameter dictionary may be empty
        if no parameters are present.

        Args:
            display_name: str, expecting a format of <test_name> followed by zero or more
            %<param>=<value> pairs.
    """

    split_display_name = display_name.split(" %")
    test_name = split_display_name[0]
    params = [p.split("=") for p in split_display_name[1:]]

    return test_name, dict(params)


def find_key_cols(row_info: 'dict | None', key_cols={}, col_name=None):
    """
        Return key columns and their values by recursively finding the innermost
        dictionary contents of given row information.

        Args:
            row_info: dict | None, contains key-value mapping information from one row.
            key_cols: dict, flattened dictionary contents from row_info.
            col_name: str | None, the name of a previous column key to be used as a prefix for new column keys.
    """

    if isinstance(row_info, dict):
        for k in row_info.keys():
            # determine new key column name
            new_col_name = "{0}_{1}".format(col_name, k) if col_name else k
            # recurse if key value is also a dict
            if isinstance(row_info.get(k), dict):
                find_key_cols(row_info.get(k), col_name=new_col_name)
            # otherwise add key-value pair to key columns dict
            else:
                key_cols[new_col_name] = row_info.get(k)
        return key_cols
    return {}


def insert_key_cols(df: pd.DataFrame, index: int, results: 'list[dict]'):
    """
    Modify a dataframe to include new columns (extracted from results) inserted at
    a given index, with names optionally prefixed by the original column name and each key.

    Args:
        df: DataFrame, to be modified by this function.
        index: int, index at which to insert new columns into the dataframe.
        results: 'list[dict]', contains key-value mapping information from all rows.
    """

    # flatten results into key columns dicts
    key_cols = [find_key_cols(r) for r in results]
    # get set of keys from all rows
    keys = set(chain.from_iterable([k.keys() for k in key_cols]))

    for k in keys:
        if k not in df.columns:
            # insert keys as new columns
            df.insert(index, k, [c.get(k) if k in c else None for c in key_cols])
            # increment index for next column insertion to maintain order
            index += 1
