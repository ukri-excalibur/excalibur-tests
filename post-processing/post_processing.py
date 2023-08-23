import argparse
import errno
import fileinput
import operator as op
import os
import re
import traceback
import math
from functools import reduce
from pathlib import Path

import pandas as pd
import yaml
from bokeh.models import Legend
from bokeh.models.sources import ColumnDataSource
from bokeh.palettes import viridis
from bokeh.plotting import figure, output_file, save
from bokeh.transform import factor_cmap

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
                    print("")
        if df.empty:
            raise FileNotFoundError(errno.ENOENT, "Could not find a valid perflog in path", log_path)

        # get axis columns
        columns = [config["x_axis"]["value"], config["y_axis"]["value"]]
        if config["x_axis"]["units"].get("column"):
            columns.insert(1, config["x_axis"]["units"]["column"])
        if config["y_axis"]["units"].get("column"):
            columns.append(config["y_axis"]["units"]["column"])

        series_columns = []
        series_filters = []
        series = config["series"]
        # extract series columns and filters
        if series:
            series_columns = [s[0] for s in series]
            series_filters = [[s[0], "==", s[1]] for s in series]
            for c in series_columns:
                if c not in columns:
                    # add series columns to column list
                    columns.append(c)

        invalid_columns = []
        # check for invalid columns
        for col in columns:
            if col not in df.columns:
                invalid_columns.append(col)
        if invalid_columns:
            raise KeyError("Could not find columns", invalid_columns)

        mask = pd.Series(df.index.notnull())
        filters = config["filters"]
        # filter rows
        if filters:
            mask = reduce(op.and_, (self.row_filter(f, df) for f in filters))
        # apply series filters
        if series_filters:
            series_mask = reduce(op.or_, (self.row_filter(f, df) for f in series_filters))
            mask = mask & series_mask
        # ensure not all rows are filtered away
        if df[mask].empty:
            raise pd.errors.EmptyDataError("Filtered dataframe is empty", df[mask].index)

        # get number of occurrences of each column
        series_col_count = {c:series_columns.count(c) for c in series_columns}
        # get number of column combinations
        series_combinations = reduce(op.mul, list(series_col_count.values()), 1)

        num_filtered_rows = len(df[mask])
        num_x_data_points = series_combinations * len(set(df[config["x_axis"]["value"]][mask]))
        # check expected number of rows
        if num_filtered_rows != num_x_data_points:
            raise RuntimeError("Unexpected number of rows ({0}) does not match number of unique x-axis values per series ({1})".format(num_filtered_rows, num_x_data_points), df[columns][mask])

        print("Selected dataframe:")
        print(df[columns][mask])

        # call a plotting script
        self.plot_generic(config["title"], df[columns][mask], config["x_axis"], config["y_axis"], series_filters)

        if self.debug & self.verbose:
            print("")
            print("Full dataframe:")
            print(df.to_json(orient="columns", indent=2))

        return df[columns][mask]

    def plot_generic(self, title, df, x_axis, y_axis, series_filters):
        """
            Create a bar chart for the supplied data using bokeh.

            Args:
                title: str, plot title (read from config).
                df: dataframe, data to plot.
                x_axis: dict, x-axis column and units (read from config).
                y_axis: dict, y-axis column and units (read from config).
                series_filters: list, x-axis groups used to filter graph data.
        """

        # get column names of axes
        x_column = x_axis.get("value")
        y_column = y_axis.get("value")
        # get units
        x_units = df[x_axis["units"]["column"]].iloc[0] if x_axis.get("units").get("column") \
                  else x_axis.get("units").get("custom")
        y_units = df[y_axis["units"]["column"]].iloc[0] if y_axis.get("units").get("column") \
                  else y_axis.get("units").get("custom")
        # determine axis labels
        x_label = "{0}{1}".format(x_column.replace("_", " ").title(),
                                  " ({0})".format(x_units) if x_units else "")
        y_label = "{0}{1}".format(y_column.replace("_", " ").title(),
                                  " ({0})".format(y_units) if y_units else "")

        # find x-axis groups (series columns)
        groups = [x_column]
        for f in series_filters:
            if f[0] not in groups:
                groups.append(f[0])
        # combine group names for later plotting with groupby
        index_group_col = "_".join(groups)
        # group by group names (or just x-axis if no other groups are present)
        grouped_df = df.groupby(x_column) if len(groups) == 1 else df.groupby(groups)
        grouped_df.apply(print)

        if self.debug:
            print("")
            print("Plot x-axis groups:")
            for key, _ in grouped_df:
                print(grouped_df.get_group(key))

        # FIXME: create html file to store plot in
        output_file(filename=os.path.join(Path(__file__).parent, "{0}.html".format(title.replace(" ", "_"))), title=title)

        # FIXME: this needs to come pre-typed (see issue #176)
        typed_y_column = df[y_column].astype(float)
        # adjust y-axis range
        min_y = 0 if min(typed_y_column) >= 0 \
                else math.floor(min(typed_y_column)*1.2)
        max_y = 0 if max(typed_y_column) <= 0 \
                else math.ceil(max(typed_y_column)*1.2)

        # create plot
        plot = figure(x_range=grouped_df, y_range=(min_y, max_y), title=title, width=800, tooltips=[(y_label, "@{0}".format("{0}_top".format(y_column)))], tools="hover", toolbar_location="above")

        # create legend outside plot
        plot.add_layout(Legend(), "right")
        # automatically base bar colouring on last group column
        colour_factors = sorted(df[groups[-1]].unique())
        # divide and assign colours
        index_cmap = factor_cmap(index_group_col, palette=viridis(len(colour_factors)), factors=colour_factors, start=len(groups)-1, end=len(groups))
        # add legend labels to data source
        print(index_group_col)
        data_source = ColumnDataSource(grouped_df).data
        print(data_source)
        legend_labels = ["{0} = {1}".format(groups[-1],group[-1]) for group in data_source[index_group_col]]
        data_source["legend_labels"] = legend_labels

        # add bars
        plot.vbar(x=index_group_col, top="{0}_top".format(y_column), width=0.9, source=data_source, line_color="white", fill_color=index_cmap, legend_field="legend_labels", hover_alpha=0.9)
        # add labels
        plot.xaxis.axis_label = x_label
        plot.yaxis.axis_label = y_label
        # adjust font size
        plot.title.text_font_size = "15pt"

        # save to file
        save(plot)

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
            mask = df[column].isnull() if operator == op.eq else df[column].notnull()
        else:
            try:
                # FIXME: dataframe column is interpreted as the same type as the supplied value
                mask = operator(df[column].astype(type(value)), value)
            except TypeError as e:
                e.args = (e.args[0] + " for column: \'{0}\' and value: \'{1}\'".format(column, value),)
                raise
            except ValueError as e:
                e.args = (e.args[0] + " in column: \'{0}\'".format(column),) + e.args[1:]
                raise

        if self.debug & self.verbose:
            print(mask)
        if self.debug:
            print("")

        return mask

def read_args():
    """
        Return parsed command line arguments.
    """

    parser = argparse.ArgumentParser(description="Plot benchmark data. At least one perflog must be supplied.")

    # required positional arguments (log path, config path)
    parser.add_argument("log_path", type=str, help="path to a perflog file or a directory containing perflog files")
    parser.add_argument("config_path", type=str, help="path to a configuration file specifying what to plot")

    # optional argument (plot type)
    parser.add_argument("-p", "--plot_type", type=str, default="generic", help="type of plot to be generated (default: \'generic\')")

    # info dump flags
    parser.add_argument("-d", "--debug", action="store_true", help="debug flag for printing additional information")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose flag for printing more debug information (must be used in conjunction with the debug flag)")

    return parser.parse_args()

def read_config(path):
    """
        Return a dictionary containing configuration information for plotting.

        Args:
            path: str, path to a config file.
    """

    with open(path, "r") as file:
        config = yaml.safe_load(file)

    # check x-axis information
    if not config.get("x_axis"):
        raise KeyError("Missing x-axis information")
    if not config.get("x_axis").get("value"):
        raise KeyError("Missing x-axis value information")
    if not config.get("x_axis").get("units"):
        raise KeyError("Missing x-axis units information")
    # check y-axis information
    if not config.get("y_axis"):
        raise KeyError("Missing y-axis information")
    if not config.get("y_axis").get("value"):
        raise KeyError("Missing y-axis value information")
    if not config.get("y_axis").get("units"):
        raise KeyError("Missing y-axis units information")

    # check series length
    if config.get("series") is None:
        raise KeyError("Missing series information (specify an empty list [] if there is only one series)")
    if len(config["series"]) == 1:
        raise KeyError("Number of series must be >= 2 (specify an empty list [] if there is only one series)")

    # check filters are present
    if config.get("filters") is None:
        raise KeyError("Missing filters information (specify an empty list [] if none are required)")

    # check plot title information
    if not config.get("title"):
        raise KeyError("Missing plot title information")

    return config

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
            e.args = (e.args[0] + " in file \'{0}\':".format(path),) + e.args[1:]
            raise

    return pd.DataFrame.from_records(records)

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
