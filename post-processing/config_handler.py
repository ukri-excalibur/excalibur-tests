import yaml


class ConfigHandler:

    def __init__(self, config: dict):

        # validate dict structure
        config = read_config(config)
        # extract config information
        self.title = config.get("title")
        self.x_axis = config.get("x_axis")
        self.y_axis = config.get("y_axis")
        self.filters = config.get("filters")
        self.series = config.get("series")
        self.column_types = config.get("column_types")

        # parse filter information
        self.and_filters = []
        self.or_filters = []
        self.series_filters = []
        self.parse_filters()

        # parse scaling information
        self.scaling_column = None
        self.scaling_custom = None
        self.parse_scaling()

        # find relevant columns
        self.series_columns = []
        self.plot_columns = []
        self.all_columns = []
        self.parse_columns()

    @classmethod
    def from_path(cfg_hand, config_path):
        return cfg_hand(open_config(config_path))

    def get_filters(self):
        return self.and_filters, self.or_filters, self.series_filters

    def get_y_scaling(self):
        return self.scaling_column, self.scaling_custom

    def parse_filters(self):
        """
            Store filtering information from filters and series.
        """

        # filters
        if self.filters:
            if self.filters.get("and"):
                self.and_filters = self.filters.get("and")
            if self.filters.get("or"):
                self.or_filters = self.filters.get("or")

        # series filters
        if self.series:
            self.series_filters = [[s[0], "==", s[1]] for s in self.series]

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
        self.plot_columns = [self.x_axis.get("value"), self.x_axis["units"].get("column"),
                             self.y_axis.get("value"), self.y_axis["units"].get("column")]

        # FIXME (issue #255): allow all series values to be selected with *
        # (or if only column name is supplied)

        # series columns (duplicates not removed)
        # NOTE: currently assuming there can only be one unique series column
        self.series_columns = [s[0] for s in self.series_filters]
        # add series column to plot column list
        for s in self.series_columns:
            if s not in self.plot_columns:
                self.plot_columns.append(s)
        # drop None values
        self.plot_columns = [c for c in self.plot_columns if c is not None]

        # filter columns (duplicates not removed)
        filter_columns = [f[0] for f in self.and_filters] + [f[0] for f in self.or_filters]

        # all typed columns
        self.all_columns = set(self.plot_columns + filter_columns +
                               ([self.scaling_column.get("name")] if self.scaling_column else []))


def open_config(path):
    """
        Return a dictionary containing configuration information for plotting.

        Args:
            path: path, path to yaml config file.
    """

    with open(path, "r") as file:
        return yaml.safe_load(file)


def read_config(config):
    """
        Check required configuration information. At least plot title, x-axis,
        y-axis, and column types must be present.

        Args:
            config: dict, config information.
    """

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
        elif not config.get("y_axis").get("scaling").get("custom"):
            raise RuntimeError("Invalid custom scaling value (cannot divide by {0})."
                               .format(config.get("y_axis").get("scaling").get("custom")))

    # check optional series information
    if config.get("series"):
        if len(config.get("series")) == 1:
            raise RuntimeError("Number of series must be >= 2.")
        if len(set([s[0] for s in config.get("series")])) > 1:
            raise RuntimeError("Currently supporting grouping of series by only one column. \
                               Please use a single column name in your series configuration.")

    # check column types information
    if not config.get("column_types"):
        raise KeyError("Missing column types information.")

    return config
