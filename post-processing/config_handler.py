import yaml


class ConfigHandler:

    def __init__(self, config: dict):

        self.title = config.get("title")
        self.x_axis = config.get("x_axis")
        self.y_axis = config.get("y_axis")
        self.filters = config.get("filters")
        self.series = config.get("series")
        self.column_types = config.get("column_types")

        # get column and filter information
        self.get_filters()
        self.get_columns()

    def get_filters(self):
        """
            Store filtering information from filters and series.
        """
        # filters
        self.and_filters = []
        self.or_filters = []
        if self.filters:
            if self.filters.get("and"):
                self.and_filters = self.filters.get("and")
            if self.filters.get("or"):
                self.or_filters = self.filters.get("or")

        # series filters
        self.series_filters = [[s[0], "==", s[1]] for s in self.series] if self.series else []

    def get_columns(self):
        """
            Store all necessary dataframe columns for plotting and filtering.
        """

        # axis columns
        self.plot_columns = [self.x_axis.get("value"), self.x_axis["units"].get("column"),
                             self.y_axis.get("value"), self.y_axis["units"].get("column")]

        # FIXME: allow all series values to be selected with *
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
        self.filter_columns = [f[0] for f in self.and_filters] + [f[0] for f in self.or_filters]

        # FIXME: add scaling for x-axis
        self.scaling_column = None
        # scaling column
        if self.y_axis.get("scaling"):
            if self.y_axis.get("scaling").get("column"):
                self.scaling_column = self.y_axis["scaling"]["column"].get("name")

        # all typed columns
        self.all_columns = set(self.plot_columns + self.filter_columns +
                               ([self.scaling_column] if self.scaling_column else []))


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
        if (config.get("y_axis").get("scaling").get("column") is not None and
            config.get("y_axis").get("scaling").get("custom") is not None):
            raise RuntimeError(
                "Specify y-axis scaling information as only one of 'column' or 'custom'.")

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
