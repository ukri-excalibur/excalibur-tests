from pathlib import Path

import yaml


class ConfigHandler:

    def __init__(self, config: dict, template=False):
        """
            Initialise class.

            Args:
                config: dict, plot configuration information.
                template: bool, flag to skip config validation (unsafe).
        """

        if not template:
            # validate dict structure
            config = read_config(config)

        # extract config information
        self.plot_type = config.get("plot_type")
        self.title = config.get("title")
        self.x_axis = config.get("x_axis")
        self.y_axis = config.get("y_axis")
        self.filters = config.get("filters")
        self.series = config.get("series")
        self.column_types = config.get("column_types")
        self.extra_columns = config.get("extra_columns_to_csv")

        # parse filter information
        self.and_filters = []
        self.or_filters = []
        self.series_filters = []
        self.to_string_filter_vals()
        self.parse_filters()

        # parse scaling information
        self.scaling_column = None
        self.scaling_custom = None
        self.parse_scaling()

        # find relevant columns
        self.series_columns = []
        self.filter_columns = []
        self.plot_columns = []
        self.all_columns = []
        self.parse_columns()

    @classmethod
    def from_path(self, config_path: Path, template=False):
        """
            Initialise class from a path.
        """
        return self(open_config(config_path), template)

    @classmethod
    def from_template(self):
        """
            Initialise class from an empty template. Skips config validation.
        """

        return self(dict({
            "plot_type": None,
            "title": None,
            "x_axis": {"value": None, "units": {"custom": None},
                       "range": {"use_default": True, "min": None, "max": None}},
            "y_axis": {"value": None, "units": {"custom": None},
                       "scaling": {"custom": None},
                       "range": {"use_default": True, "min": None, "max": None}},
            "filters": {"and": [], "or": []},
            "series": [],
            "column_types": {},
            "extra_columns_to_csv": []}), template=True)

    def get_filters(self):
        """
            Return and, or, and series filter lists.
        """
        return self.and_filters, self.or_filters, self.series_filters

    def get_y_scaling(self):
        """
            Return column and custom scaling information.
        """
        return self.scaling_column, self.scaling_custom

    def to_string_filter_vals(self):
        """
            Store filter values as their string representations for internal consistency.
        """

        # filters
        if self.filters:
            self.filters["and"] = ([[f[0], f[1], str(f[2])] for f in self.filters["and"]]
                                   if self.filters.get("and") else [])
            self.filters["or"] = ([[f[0], f[1], str(f[2])] for f in self.filters["or"]]
                                  if self.filters.get("or") else [])

        # series
        self.series = [[s[0], str(s[1])] for s in self.series] if self.series else []

    def parse_filters(self):
        """
            Store filtering information from filters and series.
        """

        # filters
        if self.filters:
            # FIXME (issue #314): consider a better way of doing this
            # use hashable tuples to remove duplicate filters
            self.and_filters = (list(dict.fromkeys([tuple(f) for f in self.filters["and"]]))
                                if self.filters.get("and") else [])
            self.or_filters = (list(dict.fromkeys([tuple(f) for f in self.filters["or"]]))
                               if self.filters.get("or") else [])
            # convert back to lists to maintain mutability
            self.and_filters = [list(f) for f in self.and_filters]
            self.or_filters = [list(f) for f in self.or_filters]
            # FIXME (issue #314): consider the purpose of keeping multiple filter lists
            self.filters["and"] = self.and_filters
            self.filters["or"] = self.or_filters

        # series filters
        self.series_filters = (list(dict.fromkeys([(s[0], "==", s[1]) for s in self.series]))
                               if self.series else [])
        self.series_filters = [list(s) for s in self.series_filters]
        self.series = [[s[0], s[-1]] for s in self.series]

    def parse_scaling(self):
        """
            Store scaling information for numeric axes.
        """

        # FIXME (issue #182): add scaling for x-axis
        if self.y_axis.get("scaling"):
            # scaling column
            self.scaling_column = self.y_axis.get("scaling").get("column")
            # custom scaling value
            self.scaling_custom = self.y_axis.get("scaling").get("custom")

    def parse_columns(self):
        """
            Store all necessary dataframe columns for plotting and filtering.
        """

        # axis columns
        self.plot_columns = [self.x_axis.get("value"),
                             self.x_axis["units"].get("column") if self.x_axis.get("units") else None,
                             self.y_axis.get("value"),
                             self.y_axis["units"].get("column") if self.y_axis.get("units") else None]

        # FIXME (issue #255): allow all series values to be selected with *
        # (or if only column name is supplied)

        # series columns
        # NOTE: currently assuming there can only be one unique series column
        self.series_columns = (list(dict.fromkeys([s[0] for s in self.series_filters]))
                               if self.series_filters else [])
        # add series column to plot column list
        for s in self.series_columns:
            if s not in self.plot_columns:
                self.plot_columns.append(s)
        # drop None values
        self.plot_columns = list(dict.fromkeys([c for c in self.plot_columns if c is not None]))

        # extra columns
        self.extra_columns = (list(dict.fromkeys(self.extra_columns)) if self.extra_columns else [])
        # remove duplicated columns from the extra columns list
        extra_duplicates = set(self.plot_columns) & set(self.extra_columns)
        for d in extra_duplicates:
            self.extra_columns.remove(d)

        # filter columns
        self.filter_columns = (list(dict.fromkeys([f[0] for f in self.and_filters] +
                                                  [f[0] for f in self.or_filters]))
                               if self.and_filters or self.or_filters else [])

        # all typed columns
        self.all_columns = list(
            dict.fromkeys(self.plot_columns + self.filter_columns +
                          ([self.scaling_column.get("name")] if self.scaling_column else [])))

    def remove_redundant_types(self):
        """
            Check for columns that are no longer in use and remove them from the type dict.
        """

        column_types = self.column_types.copy()
        for col in column_types:
            if col not in self.all_columns:
                self.column_types.pop(col, None)

    def to_dict(self):
        """
            Convert information in the class to a dictionary.
        """

        return dict({
            "plot_type": self.plot_type,
            "title": self.title,
            "x_axis": self.x_axis,
            "y_axis": self.y_axis,
            "filters": self.filters,
            "series": self.series,
            "column_types": self.column_types,
            "extra_columns_to_csv": self.extra_columns})

    def to_yaml(self):
        """
            Convert information in the class to a yaml format.
        """
        return yaml.dump(self.to_dict(), default_flow_style=None, sort_keys=False)


def open_config(path: Path):
    """
        Return a dictionary containing configuration information for plotting
        from the path to a yaml file.

        Args:
            path: Path, path to yaml config file.
    """
    with open(path, "r") as file:
        return load_config(file)


def load_config(file):
    """
        Return a loaded config dictionary from a yaml file.

        Args:
            file: file, config yaml.
    """
    return yaml.safe_load(file)


def read_config(config: dict):
    """
        Check required configuration information. At least plot title, x-axis,
        y-axis, and column types must be present.

        Args:
            config: dict, plot configuration information.
    """

    # check plot_type information
    plot_type = config.get("plot_type")
    if not plot_type:
        raise KeyError("Missing plot type information.")
    elif (plot_type != 'generic') and (plot_type != 'line'):
        raise RuntimeError("Plot type must be one of 'generic' or 'line'.")

    # check plot title information
    if not config.get("title"):
        raise KeyError("Missing plot title information.")

    # check x-axis information
    if not config.get("x_axis"):
        raise KeyError("Missing x-axis information.")
    if not config.get("x_axis").get("value"):
        raise KeyError("Missing x-axis value information.")
    if not config.get("x_axis").get("units"):
        raise KeyError("Missing x-axis units information.")
    if not config.get("x_axis").get("range"):
        raise KeyError("Missing x-axis range information.")
    if (config.get("x_axis").get("units").get("column") is not None and
        config.get("x_axis").get("units").get("custom") is not None):
        raise RuntimeError(
            "Specify x-axis units information as only one of 'column' or 'custom'.")

    # check y-axis information
    if not config.get("y_axis"):
        raise KeyError("Missing y-axis information.")
    if not config.get("y_axis").get("value"):
        raise KeyError("Missing y-axis value information.")
    if not config.get("y_axis").get("units"):
        raise KeyError("Missing y-axis units information.")
    if not config.get("y_axis").get("range"):
        raise KeyError("Missing y-axis range information.")
    if (config.get("y_axis").get("units").get("column") is not None and
        config.get("y_axis").get("units").get("custom") is not None):
        raise RuntimeError(
            "Specify y-axis units information as only one of 'column' or 'custom'.")

    # check optional scaling information
    if config.get("y_axis").get("scaling"):
        if config.get("y_axis").get("scaling").get("column") is not None:
            if config.get("y_axis").get("scaling").get("custom") is not None:
                raise RuntimeError(
                    "Specify y-axis scaling information as only one of 'column' or 'custom'.")
            if not config.get("y_axis").get("scaling").get("column").get("name"):
                raise RuntimeError("Scaling column must have a name.")
        elif (config.get("y_axis").get("scaling").get("custom") is not None and
              not config.get("y_axis").get("scaling").get("custom")):
            raise RuntimeError("Invalid custom scaling value (cannot divide by {0})."
                               .format(config.get("y_axis").get("scaling").get("custom")))

    # check optional series information
    if config.get("series"):
        if plot_type == 'generic':
            if len(config.get("series")) == 1:
                raise RuntimeError("Number of series must be >= 2 for generic plot.")
        if plot_type == 'line':
            if len(config.get("series")) < 1:
                raise RuntimeError("Number of series must be >= 1 for line plot.")
        if len(set([s[0] for s in config.get("series")])) > 1:
            raise RuntimeError("Currently supporting grouping of series by only one column. \
                               Please use a single column name in your series configuration.")

    # check column types information
    if not config.get("column_types"):
        raise KeyError("Missing column types information.")

    return config
