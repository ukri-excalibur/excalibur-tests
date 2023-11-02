## Benchmark Results Post-Processing

### Overview

The post-processing scripts provided with the ExCALIBUR tests package are intended to grant users a quick starting point for visualising benchmark results with basic graphs and tables. Their components can also be used inside custom users' scripts.

There are three main post-processing components:
- **`Perflog parsing`:**
  - Data from benchmark performance logs are stored in a pandas DataFrame.
- **`Data filtering`:**
  - If more than one perflog is used for plotting, DataFrames from individual perflogs are concatenated together into one DataFrame.
  - The DataFrame is then filtered, keeping only relevant rows and columns.
- **`Plotting`:**
  - A filtered DataFrame is passed to a plotting script, which produces a graph and embeds it in a simple HTML file.
  - Users may run the plotting script to generate a generic bar chart. Graph settings should be specified in a configuration YAML file.

### Installation

Post-processing is an optional dependency of the ExCALIBUR tests package, as it requires Python version 3.9 or later (while the base package requires Python version 3.7 or later).

You can include post-processing in your `pip` installation of the package with the following command:

> ```pip install -e .[post-processing]```

### Usage

>```python post_processing.py log_path config_path [-p plot_type]```

- `log_path` - Path to a perflog file, or a directory containing perflog files.
- `config_path` - Path to a configuration file containing plot details.
- `plot_type` - (Optional.) Type of plot to be generated. (`Note: only a generic bar chart is currently implemented.`)

Run `post_processing.py -h` for more information (including debugging flags).

### Configuration Structure

Before running post-processing, create a config file including all necessary information for graph generation (you must specify at least plot title, x-axis, y-axis, and column types). See below for an example.

- `title` - Plot title.
- `x_axis`, `y_axis` - Axis information.
    - `value` - Axis data points. Specified with a column name.
    - `units` - Axis units. Specified either with a column name or a custom label (may be null).
- `filters` - (Optional.) Filter data rows based on specified conditions. (Specify an empty list if no filters are required.)
  - `and` - Filter mask is determined from a logical AND of conditions in list.
  - `or` - Filter mask is determined from a logical OR of conditions in list.
  - `Format: [column_name, operator, value]`
  - `Accepted operators: "==", "!=", "<", ">", "<=", ">="`
- `series` - (Optional.) Display several plots in the same graph and group x-axis data by specified column values. (Specify an empty list if there is only one series.)
  - `Format: [column_name, value]`
- `column_types` - Pandas dtype for each relevant column (axes, units, filters, series). Specified with a dictionary.
  - `Accepted types: "str"/"string"/"object", "int"/"int64", "float"/"float64", "datetime"/"datetime64"`

### Example Config

```yaml
title: "Plot Title"

x_axis:
  value: "x_axis_col"
  units:
    custom: "unit_label"

y_axis:
  value: "y_axis_col"
  units:
    column: "unit_col"

filters:
  and: [["filter_col_1", "<=", filter_val_1], ["filter_col_2", "!=", filter_val_2]]
  or: []

series: [["series_col", "series_val_1"], ["series_col", "series_val_2"]]

column_types:
  x_axis_col: "str"
  y_axis_col: "float"
  unit_col: "str"
  filter_col_1: "datetime"
  filter_col_2: "int"
  series_col: "str"
```

#### A Note on X-axis Grouping

The settings above will produce a graph that will have its x-axis data grouped based on the values in `x_axis_col` and `series_col`. (`Note: only groupings with one series column are currently supported.`) If we imagine that `x_axis_col` has two unique values, `"x_val_1"` and `"x_val_2"`, there will be four groups (and four bars) along the x-axis:

- (`x_val_1`, `series_val_1`)
- (`x_val_1`, `series_val_2`)
- (`x_val_2`, `series_val_1`)
- (`x_val_2`, `series_val_2`)

#### A Note on Filters

AND filters and OR filters are combined with a logical AND to produce the final filter mask applied to the DataFrame prior to graphing. For example:

- `and_filters` = `cond1`, `cond2`
- `or_filters`= `cond3`, `cond4`

The filters above would produce the final filter `mask` = (`cond1` AND `cond2`) AND (`cond3` OR `cond4`).

#### A Note on Column Types

All user-specified types are internally converted to their nullable incarnations. As such:

- Strings are treated as `object` (str or mixed type).
- Floats are treated as `float64`.
- Integers are treated as `Int64`.
- Datetimes are treated as `datetime64[ns]`.

#### A Note on Replaced ReFrame Columns

A perflog contains certain columns that will not be present in the DataFrame available to the graphing script. Currently, these columns are `display_name`, `extra_resources`, and `env_vars`. Removed columns should not be referenced in a plot config file.

When the row contents of `display_name` are parsed, they are separated into their constituent benchmark names and parameters. This column is replaced with a new `test_name` column and new parameter columns (if present). Similarly, the `extra_resources` and `env_vars` columns are replaced with their respective dictionary row contents (keys become columns, values become row contents).

### Future Development

The post-processing capabilities are still a work in progress. Some upcoming developments:
-  Embed graphs in GitHub Pages, instead of a bare HTML file.
-  Add scaling and regression plots.