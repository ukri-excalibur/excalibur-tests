import argparse
import errno
import fileinput
from functools import reduce
import operator as op
import os
import pandas as pd
import re
import traceback
import yaml

class PostProcessing:

    def __init__(self, debug=False, verbose=False):
        self.debug = debug
        self.verbose = verbose

    def run_post_processing(self, log_path, config):
        """
            Return a dataframe containing the information passed to a plotting script and produce relevant graphs.

            Args:
                log_path: str, path to a log file or a directory containing log files.
                config: dict, configuration information for plotting.
        """

        log_files = []
        # look for perflogs
        if os.path.isfile(log_path):
            log_files = [log_path]
        elif os.path.isdir(log_path):
            log_files = [os.path.join(root, file) for root, _, files in os.walk(log_path) for file in files]
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), log_path)

        if self.debug:
            print("")
            print("Found log files:")
            for log in log_files:
                print("-", log)
            print("")

        df = pd.DataFrame()
        # put all perflog information in one dataframe
        for file in log_files:
            try:
                temp = read_perflog(file)
                df = pd.concat([df, temp], ignore_index=True)
            except KeyError as e:
                if self.debug:
                    print("Discarding %s:" %os.path.basename(file), type(e).__name__ + ":", e.args[0], e.args[1])
        if df.empty:
            raise FileNotFoundError(errno.ENOENT, "Could not find a valid perflog in path", log_path)

        columns = config["columns"]
        REQUIRED_COLUMNS = [r"\w+_value$", r"\w+_unit$"]
        required_column_matches = [len(list(filter(re.compile(rexpr).match, columns))) > 0 for rexpr in REQUIRED_COLUMNS]
        # check for required columns
        if (len(columns) < 3) | (False in required_column_matches):
            raise KeyError("Config must contain at least 3 specified columns: a figure of merit value, a figure of merit unit, and something to plot the figure of merit against", columns)

        invalid_columns = []
        # check for invalid columns
        for col in columns:
            if col not in df.columns:
                invalid_columns.append(col)
        if invalid_columns:
            raise KeyError("Could not find columns", invalid_columns)

        filters = config["filters"]
        mask = pd.Series(df.index.notnull())
        # filter rows
        if filters:
            mask = reduce(op.and_, (self.row_filter(f, df) for f in filters))
        if df[mask].empty:
            raise pd.errors.EmptyDataError("Filtered dataframe is empty", df[mask].index)

        print("")
        print("Selected dataframe:")
        print(df[columns][mask])
        print("")

        # call a plotting script
        # TODO: plot(df, config)

        if self.debug & self.verbose:
            print("Full dataframe:")
            print(df.to_json(orient="columns", indent=2))

        return df[columns][mask]

    # operator lookup dictionary
    op_lookup = {
        "==":   op.eq,
        "!=":   op.ne,
        "<" :   op.lt,
        ">" :   op.gt,
        "<=":   op.le,
        ">=":   op.ge
    }

    def row_filter(self, filter, df: pd.DataFrame):
        """
            Return a dataframe mask based on a filter condition. The filter is a list that contains a column name, an operator, and a value (e.g. ["flops_value", ">=", 1.0]).

            Args:
                filter: list, a condition based on which a dataframe is filtered.
                df: dataframe, used to create a mask by having the filter condition applied to it.
        """

        column, str_op, value = filter
        if self.debug:
            print("Applying row filter condition:", column, str_op, value)

        # check column validity
        if column not in df.columns:
            raise KeyError("Could not find column", column)

        # check operator validity
        operator = self.op_lookup.get(str_op)
        if operator is None:
            raise KeyError("Unknown comparison operator", str_op)

        # evaluate expression and extract dataframe mask
        if value is None:
            if operator == op.eq:
                mask = df[column].isnull()
            else:
                mask = df[column].notnull()
        else:
            try:
                # dataframe column is interpreted as the same type as the supplied value
                mask = operator(df[column].astype(type(value)), value)
            except TypeError as e:
                e.args = (e.args[0] + " for column: \'{0}\' and value: \'{1}\'".format(column, value),)
                raise

        if self.debug & self.verbose:
            print(mask)

        return mask

def read_config(path):
    """
        Return a dictionary containing configuration information for plotting.

        Args:
            path: str, path to a config file.
    """

    with open(path, "r") as file:
        return yaml.safe_load(file)

def get_display_name_info(display_name):
    """
        Return a tuple containing the test name and a dictionary of parameter names and their values from the given input string. The parameter dictionary may be empty if no parameters are present.

        Args:
            display_name: str, expecting a format of <test_name> followed by zero or more %<param>=<value> pairs.
    """

    split_display_name = display_name.split(" %")
    test_name = split_display_name[0]
    params = [p.split("=") for p in split_display_name[1:]]

    return test_name, dict(params)

def prepare_columns(columns, dni):
    """
        Return a list of modified column values for a single perflog entry, after breaking up the display name column into test name and parameters. A display name index is used to determine which column to parse as the display name.

        Args:
            columns: str list, containing the column values for the whole perflog line, expecting the display name column format of <test_name> followed by zero or more %<param>=<value> pairs.
            dni: int, a display name index that identifies the display name column.
    """

    # get display name
    display_name = columns[dni]
    # get test name and parameters
    test_name, params = get_display_name_info(display_name)

    # remove display name from columns
    columns.pop(dni)
    # replace with test name and parameter values
    columns[dni:dni] = [params[name] for name in params]
    columns.insert(dni, test_name)

    return columns

# a modified and updated version of the function from perf_logs.py
def read_perflog(path):
    """
        Return a pandas dataframe from a ReFrame performance log.

        Args:
            path: str, path to log file.

        NB: This currently depends on having a non-default handlers_perflog.filelog.format in reframe's configuration. See code.

        The returned dataframe will have columns for all fields in a performance log record
        except display name, which will be broken up into test name and parameter columns.
    """

    REQUIRED_LOG_FIELDS = ["job_completion_time", r"\w+_value$", r"\w+_unit$", "display_name"]
    COLUMN_NAMES = []
    display_name_index = -1
    records = []

    with fileinput.input(path) as f:
        try:
            for line in f:

                # split columns
                columns = line.strip().split("|")

                # store perflog column names
                if fileinput.isfirstline():

                    COLUMN_NAMES = columns
                    # look for field names that match required columns
                    required_field_matches = [len(list(filter(re.compile(rexpr).match, COLUMN_NAMES))) > 0 for rexpr in REQUIRED_LOG_FIELDS]

                    # check all required columns are present
                    if False in required_field_matches:
                        raise KeyError("Perflog missing one or more required fields", REQUIRED_LOG_FIELDS)

                # determine dataframe column names
                elif fileinput.lineno() == 2:

                    # get display name index
                    display_name_index = COLUMN_NAMES.index("display_name")
                    # break up display name into test name and parameters
                    display_name = columns[display_name_index]
                    _, params = get_display_name_info(display_name)

                    # remove display name
                    COLUMN_NAMES.pop(display_name_index)
                    # replace with test name and params
                    COLUMN_NAMES[display_name_index:display_name_index] = [name for name in params]
                    COLUMN_NAMES.insert(display_name_index, "test_name")

                    # store as dictionary
                    record = dict(zip(COLUMN_NAMES, prepare_columns(columns, display_name_index)))
                    records.append(record)

                else:
                    # store as dictionary
                    record = dict(zip(COLUMN_NAMES, prepare_columns(columns, display_name_index)))
                    records.append(record)

        except Exception as e:
            e.args = (e.args[0] + " in file \'%s\':" % path,) + e.args[1:]
            raise

    return pd.DataFrame.from_records(records)

def read_args():
    """
        Return parsed command line arguments.
    """

    parser = argparse.ArgumentParser(description="Plot benchmark data. At least one perflog and figure of merit must be supplied.")

    # required positional arguments (log path, config path)
    parser.add_argument("log_path", type=str, help="path to a perflog file or a directory containing perflog files")
    parser.add_argument("config_path", type=str, help="path to a configuration file specifying what to plot")

    # optional argument (plot type)
    parser.add_argument("-p", "--plot_type", type=str, default="generic", help="type of plot to be generated (default: \'generic\')")

    # info dump flags
    parser.add_argument("-d", "--debug", action="store_true", help="debug flag for printing additional information")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose flag for printing more debug information (must be used in conjunction with the debug flag)")

    return parser.parse_args()

def main():

    args = read_args()
    post = PostProcessing(args.debug, args.verbose)

    try:
        config = read_config(args.config_path)
        post.run_post_processing(args.log_path, config)

    except Exception as e:
        print(type(e).__name__ + ":", e)
        print("Post-processing stopped")
        if args.debug:
            print(traceback.format_exc())

if __name__ == "__main__":
    main()
