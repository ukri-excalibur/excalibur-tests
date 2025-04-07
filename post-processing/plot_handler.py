import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from bokeh.models import HoverTool, Legend
from bokeh.models.sources import ColumnDataSource
from bokeh.palettes import viridis
from bokeh.plotting import figure, output_file, save
from bokeh.transform import factor_cmap
from titlecase import titlecase


def plot_generic(title, df: pd.DataFrame, x_axis, y_axis, series_filters,
                 output_path=Path(__file__).parent, debug=False):
    """
        Create a bar chart for the supplied data using bokeh.

        Args:
            title: str, plot title.
            df: dataframe, data to plot.
            x_axis: dict, x-axis column and units.
            y_axis: dict, y-axis column and units.
            series_filters: list, x-axis groups used to filter graph data.
            output_path: Path, path to a directory for storing the generated plot and csv data. Default is current directory.
            debug: bool, flag to print additional information to console.
    """

    # get column names and labels for axes
    x_column, x_label = get_axis_labels(df, x_axis, series_filters)
    y_column, y_label = get_axis_labels(df, y_axis, series_filters)

    # find x-axis groups (series columns)
    groups = [x_column]
    for f in series_filters:
        if f[0] not in groups:
            groups.append(f[0])
    # keep original x-axis dtype for sorting
    x_col_dtype = df[x_column].dtype
    last_group_dtype = df[groups[-1]].dtype
    # all x-axis data treated as categorical
    for g in groups:
        df[g] = df[g].astype(str)
    # combine group names for later plotting with groupby
    index_group_col = "_".join(groups)
    # group by group names (or just x-axis if no other groups are present)
    grouped_df = (df.groupby(x_column, sort=False) if len(groups) == 1
                  else df.groupby(groups, sort=False))

    if debug:
        print("")
        print("Plot x-axis groups:")
        for key, _ in grouped_df:
            print(grouped_df.get_group(key))

    # adjust y-axis range
    min_y = (0 if min(df[y_column]) >= 0
             else math.floor(np.nanmin(df[y_column])*1.2))
    max_y = (0 if max(df[y_column]) <= 0
             else math.ceil(np.nanmax(df[y_column])*1.2))

    # create html file to store plot in
    output_file(filename=os.path.join(
        output_path, "{0}.html".format(title.replace(" ", "_"))), title=title)

    # create plot
    plot = figure(x_range=grouped_df, y_range=(min_y, max_y), title=title,
                  width=800, toolbar_location="above")
    # configure tooltip
    plot.add_tools(HoverTool(tooltips=[
                                (y_label, "@{0}_mean".format(y_column)
                                    + ("{%0.2f}" if pd.api.types.is_float_dtype(df[y_column].dtype)
                                       else ""))],
                             formatters={"@{0}_mean".format(y_column): "printf"}))

    # sort x-axis values in descending order (otherwise default sort is ascending)
    reverse = False
    if x_axis.get("sort"):
        if x_axis["sort"] == "descending":
            reverse = True

    # sort x-axis groups by series first
    if len(groups) > 1:
        # get series values with their original dtype
        # NOTE: currently not accounting for more than one series column
        series_values = [pd.Series(x[-1], dtype=last_group_dtype).iloc[0]
                         for x in plot.x_range.factors]
        sorted_x_items = [x[1] for x in sorted(zip(series_values, plot.x_range.factors),
                                               reverse=reverse, key=lambda x: x[0])]
        plot.x_range.factors = sorted_x_items

    # sort by x-axis values
    plot.x_range.factors = sorted(plot.x_range.factors, reverse=reverse,
                                  key=lambda x: pd.Series(x[0] if len(groups) > 1 else x,
                                                          dtype=x_col_dtype).iloc[0])

    # automatically base bar colouring on last group column
    colour_factors = [str(x) for x in sorted(pd.Series(df[groups[-1]].unique(),
                                                       dtype=last_group_dtype))]
    # divide and assign colours
    index_cmap = factor_cmap(index_group_col, palette=viridis(len(colour_factors)),
                             factors=colour_factors, start=len(groups)-1, end=len(groups))
    # add legend labels to data source
    data_source = ColumnDataSource(grouped_df).data
    legend_labels = ["{0} = {1}".format(groups[-1].replace("_", " "),
                                        group[-1] if len(groups) > 1 else group)
                     for group in data_source[index_group_col]]
    data_source["legend_labels"] = legend_labels

    # create legend outside plot
    plot.add_layout(Legend(), "right")
    # add bars
    plot.vbar(x=index_group_col, top="{0}_mean".format(y_column), width=0.9, source=data_source,
              line_color="white", fill_color=index_cmap, legend_group="legend_labels", hover_alpha=0.9)
    # add labels
    plot.xaxis.axis_label = x_label
    plot.yaxis.axis_label = y_label
    # remove x-axis group ticks
    plot.xaxis.major_tick_line_color = None
    plot.xaxis.major_label_text_font_size = "0pt"
    # FIXME (#issue #255): add this as a config option at some point
    # plot.xaxis.group_label_orientation = "vertical"
    # adjust font size
    plot.title.text_font_size = "15pt"

    # get label values with their original dtype
    label_values = [pd.Series(x.label["value"].split("=")[1].strip(), dtype=last_group_dtype).iloc[0]
                    for x in plot.legend[0].items]
    # sort legend items (order determined by x-axis sort)
    sorted_legend_items = [x[1] for x in sorted(zip(label_values, plot.legend[0].items),
                                                reverse=reverse, key=lambda x: x[0])]
    plot.legend[0].items = sorted_legend_items

    # save to file
    save(plot)

    return plot


def get_axis_labels(df: pd.DataFrame, axis, series_filters):
    """
        Return the column name and label for a given axis. If a column name is supplied as
        units information, the actual units will be extracted from a dataframe.

        Args:
            df: dataframe, data to plot.
            axis: dict, axis column, units, and values to scale by.
            series_filters: list, filters for x-axis groups.
    """

    # get column name of axis
    col_name = axis.get("value")
    # get units
    units = axis.get("units").get("custom")
    if axis.get("units").get("column"):
        unit_set = set(df[axis["units"]["column"]].dropna())
        # check all rows have the same units
        if len(unit_set) != 1:
            raise RuntimeError("Unexpected number of axis unit entries {0}".format(unit_set))
        units = next(iter(unit_set))

    # get scaling information
    scaling = None
    if axis.get("scaling"):
        if axis["scaling"].get("column"):
            scaling_column = axis["scaling"]["column"]["name"]
            series_index = axis["scaling"]["column"].get("series")
            x_value = axis["scaling"]["column"].get("x_value")
            # FIXME (issue #263): make scaling label more clear
            series_col = ("{0} in {1}".format(series_filters[series_index][2], scaling_column)
                          if series_index is not None else scaling_column)
            scaling = "{0} {1}".format(x_value, series_col) if x_value else series_col
        else:
            custom = axis["scaling"].get("custom")
            scaling = str(custom) if custom else ""

    # determine axis label
    label = "{0}{1}{2}".format(titlecase(col_name.replace("_", " ")),
                               titlecase(" Scaled by {0}".format(scaling.replace("_", " ")))
                               if scaling else "",
                               " ({0})".format(units) if units else "")

    return col_name, label
