## Benchmark results post-processing

### Overview

The post-processing scripts provided with the ExCALIBUR tests package are intended to grant users a quick starting point for visualising benchmark results with basic graphs and tables. Their components can also be used inside custom users' scripts.

There are three main post-processing components:
- **`Perflog parsing:`**
  - Data from benchmark performance logs are stored in a pandas DataFrame.
- **`Data filtering:`**
  - If more than one perflog is used for plotting, DataFrames from individual perflogs are concatenated together into one DataFrame.
  - The DataFrame is then filtered, keeping only relevant rows and columns.
- **`Plotting:`**
  - A filtered DataFrame is passed to a plotting script, which produces a graph and embeds it in a simple HTML file.
  - Users may run the plotting script to generate a generic bar chart. Graph settings should be specified in a configuration YAML file.

Before running post-processing, create a config file including all necessary information for graph generation (specify at least plot title, x-axis, and y-axis). See below for an example.

### Usage

>```python post_processing.py log_path config_path [-p plot_type]```

- `log_path` - Path to a perflog file, or a directory containing perflog files.
- `config_path` - Path to a configuration file containing plot details.
- `plot_type` - (Optional.) Type of plot to be generated. (`Note: only a generic bar chart is currently implemented.`)

Run `post_processing.py -h` for more information (including debugging flags).

### Configuration Structure

- `title` - Plot title.
- `x_axis`, `y_axis` - Axis information.
    - `value` - Axis data points. Specified with a column name.
    - `units` - Axis units. Specified either with a column name or a custom label (may be null).
- `filters` - (Optional.) Filter data rows based on specified conditions. (Specify an empty list if no filters are required.)
  - `Format: [column_name, operator, value]`
  - `Accepted operators: "==", "!=", "<", ">", "<=", ">="`
- `series` - (Optional.) Display several plots in the same graph and group x-axis data by specified column values. (Specify an empty list if there is only one series.)
  - `Format: [column_name, value]`

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

filters: [["filter_col_1", "<=", "filter_val_1"], ["filter_col_2", "!=", "filter_val_2"]]

series: [["series_col", "series_val_1"], ["series_col", "series_val_2"]]
```

### Future development

The post-processing capabilities are stil a work in progress. Some upcoming developments:
-  Embed graphs in GitHub Pages, instead of a bare html file.
-  Add scaling and regression plots.