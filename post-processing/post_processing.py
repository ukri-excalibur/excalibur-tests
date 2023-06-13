import argparse
import errno
import fileinput
import os
import pandas as pd
import re

class PostProcessing:

    def __init__(self, debug=False, verbose=False):
        self.debug = debug
        self.verbose = verbose

    def run_post_processing(self, path, figures_of_merit):
        """
            Return a dataframe containing the information passed to a plotting script and produce relevant graphs.

            Args:
                path: str, path to a log file or a directory containing log files.
                figures_of_merit: str list, names of figures of merit to plot.
        """

        log_files = []
        # look for perflogs
        if os.path.isfile(path):
            log_files = [path]
        elif os.path.isdir(path):
            log_files = [os.path.join(root, file) for root, _, files in os.walk(path) for file in files]
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)

        if self.debug:
            print("Found log files:")
            for log in log_files:
                print("-", log)

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
            raise FileNotFoundError(errno.ENOENT, "Could not find a valid perflog in path", path)

        # identify a relevant subset of the dataframe to pass on
        # TODO
        columns = ["test_name", "system", "partition", "environ"]
        for fom in figures_of_merit:
            value = fom + "_value"
            unit = fom + "_unit"
            if (value in df.columns) & (unit in df.columns):
                columns.extend([value, unit])
            else:
                if self.debug:
                    print("KeyError: Could not find columns \'" + value + "\' and \'" + unit + "\'. Excluding figure of merit.")

        print("Selected dataframe:")
        print(df[columns])

        # call a plotting script
        # TODO

        if self.debug & self.verbose:
            print("Full dataframe:")
            print(df.to_json(orient="columns", indent=2))

        return df[columns]

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

    # required positional arguments (log path, figures of merit)
    parser.add_argument("log_path", type=str, help="path to a perflog file or a directory containing perflog files")
    parser.add_argument("figure_of_merit", type=str, nargs='+', help="name of figure of merit to include in plot")

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
        post.run_post_processing(args.log_path, args.figure_of_merit)
    except Exception as e:
        print("Post-processing stopped:", type(e).__name__ + ":", e)

if __name__ == "__main__":
    main()
