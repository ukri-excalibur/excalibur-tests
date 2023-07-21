## Post-Processing Tutorial

### Overview

The post-processing scripts provided with the ExCALIBUR tests package are intended to grant users a quick starting point for visualising benchmark results with basic graphs and tables.

There are three main post-processing components:
- **`Perflog parsing:`**
  - Data from benchmark performance logs are stored in a pandas DataFrame.
- **`Data filtering:`**
  - If more than one perflog is used for plotting, DataFrames from individual perflogs are concatenated together into one DataFrame.
  - The DataFrame is then filtered, keeping only relevant rows and columns.
- **`Plotting:`**
  - A filtered DataFrame is passed to a plotting script, which produces a graph and embeds it in a simple HTML file. (`TODO: Embed graphs in GitHub Pages.`)
  - Users may run the plotting script to generate a generic bar chart. Graph settings should be specified in a configuration YAML file. (`TODO: Add scaling and regression plots.`)

### Usage

>```post_processing.py log_path config_path [-p plot_type]```

- `log_path` - Path to a perflog file, or a directory containing perflog files.
- `config_path` - Path to a configuration file containing plot specifics.
- `plot_type` - (Optional.) Type of plot to be generated. (`Note: only a generic bar chart is currently implemented.`)

Run `post_processing.py -h` for more information (including debugging flags).
