## Postprocess Benchmark Results

Now let's browse the benchmark performance results, and create plots to visualise them.

**NOTE:** The post-processing package is still under development. Please refer to the latest [documentation](https://ukri-excalibur.github.io/excalibur-tests/post-processing) to use it.

----

### Postprocessing features 

The postprocessing can be performed either on a GUI or a CLI. It takes as input either a single perflog or a path that contains perflogs, and it is driven by a configuration YAML file (more on this later). Its outputs can be csv files of the whole or filtered perflog contents, as well as plots.

![Screenshot from 2024-04-25 17-01-41](https://hackmd.io/_uploads/HkWxlWOZ0.png)

We will explore its functionality features (series, filters, scaling) via the GUI first.

----

### GUI Demo

We can launch the GUI with

`streamlit run excalibur-tests/post-processing/streamlit_post_processing.py perflogs/<system>/<partition>/StreamTest.log`

Demo:
- Start without config, explore unfiltered DataFrame
- Create a plot with axes, series, filters, scaling, and extra columns
    - See how the DataFrame gets filtered/modified as values are set for those fields
    - See how those fields get modified in the configuration in real time
- Export config

Optional:
- Modify config outside the GUI
- Load it back in and generate new plot

----

### The plotting configuration file

We explored all those features in the GUI, just repeating them here for reference.

The framework contains tools to plot the FOMs of benchmarks against any of the other parameters in the perflog. This generic plotting is driven by a configuration YAML file like the one we exported from the GUI - but can also be written from scratch.

The file needs to include
- Plot title 
- Axis information
- Optional: series, filters
- Optional: scaling
- Optional: extra columns
- Data types

----

### Title and Axes

Axes must have a value specified with a DataFrame column name, and units specified with either a DataFrame column name or a custom label (including `null`).
```yaml
title: Performance vs number of tasks and CPUs_per_task

x_axis:
  value: "arraysize"
  units:
    custom: null

y_axis:
  value: "Copy_value"
  units:
    column: "Copy_unit"
```

----

### Filters

Those can be of two types: series and filters.

#### Data series

Display several data series in the same plot and group x-axis data by specified column values. Specify an empty list if you only want one series plotted. 
In our STREAM example, we have two parameters. Therefore we need to either filter down to one, or make them separate series. Let's use separate series:

Format: `[column_name, value]`
```yaml
series: [["param_cpus_per_task", "4"], ["param_cpus_per_task", "8"]]
```
**NOTE:** Currently, only one distinct `column_name` is supported. In the future, a second one will be allowed to be added. But in any case, unlimited number of series can be plotted for the same `column_name` but different `value`.

#### Filtering

You can filter data rows based on specified conditions. Those can be combined in complex ways, using the "and" and "or" filter categories. Specify an empty list for no filters.

Format: `[column_name, operator, value]`, 
Accepted operators: "==", "!=", "<", ">", "<=", ">="
```yaml
filters:
  and:
  - [job_completion_time, '>=', '2024-04-26 11:21:30']
  or: []
```

**NOTE:** After re-running the benchmarks a few times your perflog will get populated with multiple lines and you'll have to filter down to what you want to plot. Feel free to experiment with a dirtier perflog file or a folder with several perflog files.

----

### Scaling

You can scale the y axis values in various ways.

By a fixed number:
```yaml
y_axis:
  value: "Copy_value"
  units:
    column: "Copy_unit"
  scaling:
    custom: 2
```

By another column:
```yaml
y_axis:
  value: "Copy_value"
  units:
    column: "Copy_unit"
  scaling:
    column:
      name: "Add_value"
```

By one of the series:
```yaml
y_axis:
  value: "Copy_value"
  units:
    column: "Copy_unit"
  scaling:
    column:
      name: "Copy_value"
      series: 0
```
where the "series" value is the index of the series (i.e. "0" means the first series, "1" the second, and so on)

By a specific value in the column:
```yaml
y_axis:
  value: "Copy_value"
  units:
    column: "Copy_unit"
  scaling:
    column:
      name: "Copy_value"
      series: 0
      x_value: 5
```

----

### Data types

All columns used in axes, filters, and series must have a user-specified type for the data they contain. This would be the pandas dtype, e.g. `str/string/object`, `int/int64`, `float/float64`, `datetime/datetime64`.
```yaml
column_types:
  arraysize: "int"
  Copy_value: "float"
  Copy_unit: "str"
  param_cpus_per_task: "int"
  job_completion_time: "datetime"
```

----

### Extra columns

If you choose to save to a csv file the filtered DataFrame for further analysis, you can include extra columns, in addition to the ones you used for plotting. Those will not affect your plot.
```yaml
extra_columns_to_csv: ["Scale_value", "Add_value", "Triad_value"]
```

----

### Run the CLI postprocessing

Now that we have a config file, we can change it as required and run it in an automated way with new data, using the CLI:
```bash
python post_processing.py <log_path> <config_path>
```
where
- `<log_path>` is the path to a perflog file or a directory containing perflog files.
- `<config_path>` is the path to the configuration YAML file.
- other useful flags: `-s` to save the filtered DataFrame, `-np` to skip the plotting.

In our case,
```bash
python excalibur-tests/post-processing/post_processing.py -s perflogs/archer2/compute-node/StreamTest.log ~/Downloads/Plotyplot.yaml
```

----

### View the Output

And behold! Inside `excalibur-tests/post-processing`, we've generated the same plot and the csv file with the data it contains, in a reproducible way!

![bokeh_plot](https://hackmd.io/_uploads/BJbgNxgGA.png)

