import argparse
import json
import traceback
from pathlib import Path

import streamlit as st
from config_handler import ConfigHandler, load_config, read_config
from post_processing import PostProcessing
from streamlit_bokeh import streamlit_bokeh

# drop-down lists
operators = ["==", "!=", "<", ">", "<=", ">="]
column_types = ["datetime", "int", "float", "str"]
filter_types = ["and", "or", "series"]
# pandas to user type mapping
type_lookup = {"datetime64[ns]": "datetime",
               "float64": "float",
               "Float64": "float",
               "int64": "int",
               "Int64": "int",
               "object": "str"}
# user to pandas type mapping
dtype_lookup = {"datetime": "datetime64[ns]",
                "float": "float64",
                "int": "Int64",
                "str": "object"}


def update_ui(post: PostProcessing, config: ConfigHandler, e: 'Exception | None' = None):
    """
        Create an interactive user interface for post-processing using Streamlit.

        Args:
            post: PostProcessing, class containing performance log data and filter information.
            config: ConfigHandler, class containing configuration information for plotting.
            e: Exception | None, a potential config validation error (only used for user information).
    """

    # stop the session state from resetting each time this function is run
    state = st.session_state
    if state.get("post") is None:
        state.post = post
        state.config = config
        # display initial config validation error, if present, and clear upon page reload
        if e:
            st.exception(e)

    post = state.post
    config = state.config

    # display graph
    if post.plot:
        streamlit_bokeh(post.plot, use_container_width=True, theme="streamlit")

    # display dataframe data
    show_df = st.toggle("Show DataFrame")
    if show_df:
        try:
            if len(config.plot_columns + config.extra_columns) > 0:
                st.dataframe(post.df[post.mask][config.plot_columns + config.extra_columns],
                             hide_index=True, use_container_width=True)
            else:
                st.dataframe(post.df[post.mask], hide_index=True, use_container_width=True)
        except Exception as e:
            st.exception(e)

    # display config in current session state
    show_config = st.toggle("Show Config", key="show_config")
    if show_config:
        st.write(config.to_dict())

    # display config information
    with st.sidebar:

        # config file uploader
        st.file_uploader("Upload Config", type="yaml", key="uploaded_config", on_change=update_config)

        # set plot title
        if "title" not in state:
            state["title"] = config.title
        title = st.text_input("#### Title", placeholder="None", key="title")
        if title != config.title:
            config.title = title
        # warn if title is blank
        if not title:
            st.warning("Missing plot title information.")

        # style expander labels as markdown h6
        # and hover colour as that of the multiselect labels
        st.markdown(
            """<style>
                div[data-testid="stExpander"] details summary span div p{
                    font-size: 12px;
                    font-weight: 600;
                }
                [data-testid="stExpander"] details:hover summary{
                    background-color: rgba(255, 75, 75, 0.1);
                }
            </style>""",
            unsafe_allow_html=True)

        # display axis options
        axis_options()
        # display filter options
        filter_options()

        generate_graph, download_config = st.columns(2)
        # re-run post processing and create a new plot
        with generate_graph:
            st.button("Generate Graph", on_click=rerun_post_processing, use_container_width=True)
        # download session state config
        with download_config:
            if config.title:
                st.download_button("Download Config", config.to_yaml(),
                                   "{0}_config.yaml".format((config.title).lower().replace(" ", "_")),
                                   on_click=validate_download_config, use_container_width=True)
            else:
                st.button("Download Config", disabled=True, use_container_width=True)


def update_config():
    """
        Change session state config to uploaded config file.
    """

    state = st.session_state
    uploaded_config = state.uploaded_config
    df = state.post.df

    if uploaded_config:
        try:
            config_dict = load_config(uploaded_config)
            state.config = ConfigHandler(config_dict)
            config = state.config

            # inputs that may have a default None value should be changed here
            state.title = config.title

            # x-axis
            if config.x_axis.get("value") in df.columns:
                state.x_axis_column = config.x_axis.get("value")
            else:
                st.warning("Assigned x-axis column is not in the DataFrame.")
            # x units
            if config.x_axis.get("units"):
                if config.x_axis["units"].get("column") in df.columns:
                    state.x_axis_units_column = config.x_axis["units"].get("column")
                elif config.x_axis["units"].get("column") is not None:
                    st.warning("Assigned x-axis units column is not in the DataFrame.")
                state.x_axis_units_custom = config.x_axis["units"].get("custom")

            # y-axis
            if config.y_axis.get("value") in df.columns:
                state.y_axis_column = config.y_axis.get("value")
            else:
                st.warning("Assigned y-axis column is not in the DataFrame.")
            # y units
            if config.y_axis.get("units"):
                if config.y_axis["units"].get("column") in df.columns:
                    state.y_axis_units_column = config.y_axis["units"].get("column")
                elif config.y_axis["units"].get("column") is not None:
                    st.warning("Assigned y-axis units column is not in the DataFrame.")
                state.y_axis_units_custom = config.y_axis["units"].get("custom")

            # y scaling
            if config.y_axis.get("scaling"):
                if config.y_axis["scaling"].get("column"):
                    # y scaling column
                    if config.y_axis["scaling"]["column"].get("name") in df.columns:
                        state.y_axis_scaling_column = config.y_axis["scaling"]["column"].get("name")
                    else:
                        st.warning("Assigned y-axis scaling column is not in the DataFrame.")
                    # y scaling series
                    series_index = config.y_axis["scaling"]["column"].get("series")
                    if series_index is not None:
                        if isinstance(series_index, int):
                            if 0 <= series_index < len(config.series_filters):
                                state.y_axis_scaling_series = config.series_filters[series_index]
                            else:
                                st.warning("Assigned series index is out of range.")
                        else:
                            st.warning("Assigned series index is not an integer.")
                    # y scaling x-axis value
                    x_value = config.y_axis["scaling"]["column"].get("x_value")
                    if config.x_axis.get("value") in df.columns:
                        # ensure types match for accurate comparison
                        if x_value in df[config.x_axis.get("value")].copy().astype(
                                dtype_lookup.get(type(x_value))).values:
                            state.y_axis_scaling_x_value = x_value
                        else:
                            st.warning("Assigned scaling x value is not in the x-axis column.")
                state.y_axis_custom_scaling_val = (str(config.y_axis["scaling"].get("custom"))
                                                   if config.y_axis["scaling"].get("custom") else None)

            # update dataframe types
            if all([c in df.columns for c in config.all_columns]):
                state.post.apply_df_types(config.all_columns, config.column_types)

        except Exception as e:
            st.exception(e)
            state.post.plot = None
            # autofill some information from invalid config
            try:
                state.config = ConfigHandler(config_dict, template=True)
            except Exception as e:
                st.exception(e)


def axis_options():
    """
        Display axis options interface.
    """

    config = st.session_state.config
    st.write("#### Axis Options")

    with st.container(border=True):
        # x-axis select
        axis_select("x", config.x_axis)
    with st.container(border=True):
        # y-axis select
        axis_select("y", config.y_axis)

    # apply changes
    update_axes()


def axis_select(label: str, axis: dict):
    """
        Allow the user to select axis column and type for post-processing.

        Args:
            label: str, axis label (either 'x' or 'y').
            axis: dict, axis column, units, and scaling from config.
    """

    state = st.session_state
    df = state.post.df
    # default drop-down selections
    type_index = 0
    column_index = None
    if axis.get("value") in df.columns:
        type_index = column_types.index(type_lookup.get(str(df[axis["value"]].dtype)))
        column_index = list(df.columns).index(axis["value"])

    # axis information drop-downs
    axis_type, axis_column = st.columns(2)
    # type select
    with axis_type:
        st.selectbox("{0}-axis column type".format(label), column_types,
                     key="{0}_axis_type".format(label), index=type_index)
    # column select
    with axis_column:
        if "{0}_axis_column".format(label) not in state:
            state["{0}_axis_column".format(label)] = df.columns[column_index] if column_index is not None else None
        st.selectbox("{0}-axis column".format(label), df.columns, placeholder="None",
                     key="{0}_axis_column".format(label))
    # warn if no axis column is selected
    if not st.session_state["{0}_axis_column".format(label)]:
        st.warning("Missing {0}-axis value information.".format(label))

    # units select
    with st.expander("Units"):
        units_select(label, axis)
    # scaling select
    if label == "y":
        with st.expander("Scaling"):
            scaling_select(axis)

    # sort checkbox
    if label == "x":
        st.checkbox("sort descending", True if axis.get("sort") == "descending" else False,
                    key="{0}_axis_sort".format(label))

    # log checkbox
    if (st.session_state["{0}_axis_type".format(label)] == "float" or
        st.session_state["{0}_axis_type".format(label)] == "int"):
        st.checkbox("logarithmic axis", True if axis.get("logarithmic") else False,
                    key="{0}_axis_log".format(label))
    else:
        # set checkbox to false if already in session state
        if "{0}_axis_log".format(label) in st.session_state:
            st.session_state["{0}_axis_log".format(label)] = False
        # disable for non-numeric axis types
        st.checkbox("logarithmic axis", False, disabled=True, key="{0}_axis_log".format(label))


def units_select(label: str, axis: dict):
    """
        Allow the user to select or specify axis units for post-processing.

        Args:
            label: str, axis label (either 'x' or 'y').
            axis: dict, axis column, units, and scaling from config.
    """

    state = st.session_state
    df = state.post.df
    # default drop-down selection
    units_index = None
    if axis.get("units"):
        if axis["units"].get("column") in df.columns:
            units_index = list(df.columns).index(axis["units"]["column"])

    units_column, units_custom = st.columns(2)
    # units select
    with units_column:
        if "{0}_axis_units_column".format(label) not in state:
            state["{0}_axis_units_column".format(label)] = df.columns[units_index] if units_index is not None else None
        st.selectbox("{0}-axis units column".format(label), df.columns, placeholder="None",
                     key="{0}_axis_units_column".format(label))
    # set custom units
    with units_custom:
        if "{0}_axis_units_custom".format(label) not in state:
            state["{0}_axis_units_custom".format(label)] = axis["units"].get("custom") if axis.get("units") else None
        st.text_input("{0}-axis units custom".format(label), placeholder="None",
                      key="{0}_axis_units_custom".format(label),
                      help="Assign a custom units label. Will clear the units column selection.")

    st.button("Clear Units", key="clear_{0}_axis_units".format(label), on_click=clear_fields,
              args=[["{0}_axis_units_column".format(label), "{0}_axis_units_custom".format(label)]])


def clear_fields(field_keys: 'list[str]'):
    """
        Reset the state of all provided fields to None.

        Args:
            field_keys: list, keys of fields in the session state.
    """

    for k in field_keys:
        st.session_state[k] = None


def scaling_select(axis: dict):
    """
        Allow the user to select or specify axis scaling for post-processing.

        Args:
            axis: dict, axis column, units, and scaling from config.
    """

    state = st.session_state
    df = state.post.df

    # scaling value selection columns
    series_col = state.config.series_filters
    x_col = (list(df[state.post.mask][state.x_axis_column].drop_duplicates().sort_values())
             if state.x_axis_column else [])

    # default drop-down selections
    type_index = 0
    scaling_index = None
    series_index = None
    x_index = None
    if axis.get("scaling"):
        if axis["scaling"].get("column"):
            if axis["scaling"]["column"].get("name") in df.columns:
                type_index = column_types.index(type_lookup.get(str(df[axis["scaling"]["column"]["name"]].dtype)))
                scaling_index = list(df.columns).index(axis["scaling"]["column"]["name"])
            if isinstance(axis["scaling"]["column"].get("series"), int):
                if 0 <= axis["scaling"]["column"].get("series") < len(series_col):
                    series_index = int(axis["scaling"]["column"]["series"])
            if axis["scaling"]["column"].get("x_value") and len(x_col) > 0:
                if axis["scaling"]["column"]["x_value"] in x_col:
                    x_index = x_col.index(axis["scaling"]["column"]["x_value"])

    c1, c2 = st.columns(2)
    with c1:
        st.selectbox("scaling column type", column_types,
                     key="y_axis_scaling_type", index=type_index)
    with c2:
        if "y_axis_scaling_column" not in state:
            state["y_axis_scaling_column"] = df.columns[scaling_index] if scaling_index is not None else None
        st.selectbox("scaling column", df.columns, placeholder="None",
                     key="y_axis_scaling_column")

    c1, c2 = st.columns(2)
    with c1:
        if "y_axis_scaling_series" not in state:
            state["y_axis_scaling_series"] = series_col[series_index] if series_index is not None else None
        st.selectbox("scaling series", series_col, placeholder="None",
                     key="y_axis_scaling_series")
    with c2:
        if "y_axis_scaling_x_value" not in state:
            state["y_axis_scaling_x_value"] = x_col[x_index] if x_index is not None else None
        st.selectbox("scaling x-axis value", x_col, placeholder="None",
                     key="y_axis_scaling_x_value")

    if "y_axis_custom_scaling_val" not in state:
        state["y_axis_custom_scaling_val"] = (str(axis["scaling"].get("custom")) if axis["scaling"].get("custom")
                                              else None if axis.get("scaling") else None)
    st.text_input("custom scaling value", placeholder="None", key="y_axis_custom_scaling_val",
                  help="Assign a scaling value that isn't in the data. Will clear all other scaling selections.")

    st.button("Clear Scaling", on_click=clear_fields, args=[["y_axis_scaling_column", "y_axis_scaling_series",
                                                             "y_axis_scaling_x_value", "y_axis_custom_scaling_val"]])


def update_axes():
    """
        Apply user-selected axis columns and types to session state config.
    """

    state = st.session_state
    config = state.config

    x_column = state.x_axis_column
    x_units_column = state.x_axis_units_column
    x_units_custom = state.x_axis_units_custom
    x_sort = state.x_axis_sort
    x_log = state.x_axis_log

    y_column = state.y_axis_column
    y_units_column = state.y_axis_units_column
    y_units_custom = state.y_axis_units_custom
    y_scaling_column = state.y_axis_scaling_column
    y_scaling_series = state.y_axis_scaling_series
    y_scaling_x = state.y_axis_scaling_x_value
    y_scaling_custom = state.y_axis_custom_scaling_val
    y_log = state.y_axis_log

    # update columns
    config.x_axis["value"] = x_column
    config.y_axis["value"] = y_column
    # update column types
    config.column_types[x_column] = state.x_axis_type
    config.column_types[y_column] = state.y_axis_type

    # update units
    # NOTE: units are automatically interpreted as strings for simplicity
    config.x_axis["units"] = {"custom": x_units_custom}
    if not x_units_custom and x_units_column:
        config.x_axis["units"] = {"column": x_units_column}
        config.column_types[x_units_column] = "str"
    config.y_axis["units"] = {"custom": y_units_custom}
    if not y_units_custom and y_units_column:
        config.y_axis["units"] = {"column": y_units_column}
        config.column_types[y_units_column] = "str"

    # update scaling
    config.y_axis["scaling"] = {"custom": json.loads(str(y_scaling_custom)) if y_scaling_custom else None}
    if not y_scaling_custom and y_scaling_column:
        # NOTE: series index needs to be kept as int for now
        config.y_axis["scaling"] = {"column": {"name": y_scaling_column,
                                               "series": (state.config.series_filters.index(y_scaling_series)
                                                          if y_scaling_series else None),
                                               "x_value": json.loads(str(y_scaling_x)) if y_scaling_x else None}}
        config.column_types[y_scaling_column] = state.y_axis_scaling_type

    config.parse_scaling()
    # update types after changing axes
    update_types()

    # update sort and log
    config.x_axis["sort"] = "descending" if x_sort else "ascending"
    config.x_axis["logarithmic"] = x_log
    config.y_axis["logarithmic"] = y_log


def update_types():
    """
        Apply user-selected types to session state config and dataframe.
    """

    post = st.session_state.post
    config = st.session_state.config
    df = st.session_state.post.df

    # re-parse column names
    config.parse_columns()
    # remove redundant types from config
    config.remove_redundant_types()
    if all([c in df.columns for c in config.all_columns]):
        try:
            # update dataframe types
            post.apply_df_types(config.all_columns, config.column_types)
        except Exception as e:
            st.exception(e)
            post.plot = None


def filter_options():
    """
        Display filter options interface.
    """

    st.write("#### Filter Options")
    # allow wide multiselect labels
    # but hidden overflow for selectboxes
    st.markdown(
        """<style>
            .stMultiSelect
            [data-baseweb=select] span{
                max-width: inherit;
            }
            [data-baseweb=select] div{
                overflow: auto;
            }
            .stSelectbox
            [data-baseweb=select] div{
                overflow: hidden;
            }
        </style>""",
        unsafe_allow_html=True)

    # display current filters
    current_filters()
    # display new filter addition options
    new_filter_options()
    # display current extra columns
    extra_columns()
    # display new extra column addition options
    new_extra_column_options()


def current_filters():
    """
        Display current filters.
    """

    config = st.session_state.config
    st.write("###### Current AND Filters")
    st.multiselect("AND Filters", config.and_filters if config.and_filters else [None],
                   config.and_filters, key="and", on_change=update_filter,
                   args=["and"], placeholder="None", label_visibility="collapsed")

    st.write("###### Current OR Filters")
    st.multiselect("OR Filters", config.or_filters if config.or_filters else [None],
                   config.or_filters, key="or", on_change=update_filter,
                   args=["or"], placeholder="None", label_visibility="collapsed")

    st.write("###### Current Series")
    st.multiselect("Series", config.series if config.series else [None],
                   config.series, key="series", on_change=update_filter,
                   args=["series"], placeholder="None", label_visibility="collapsed")


def new_filter_options():
    """
        Display new filter addition options interface.
    """

    state = st.session_state
    post = state.post
    with st.expander("Add New Filter"):

        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("filter type", filter_types, key="filter_type")
        with c2:
            st.selectbox("filter column type", column_types, key="filter_column_type")

        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("filter column", post.df.columns, key="filter_col")
        with c2:
            if state.filter_type == "series":
                st.selectbox("operator", ["=="], key="filter_op")
            else:
                st.selectbox("operator", operators, key="filter_op")

        c1, c2 = st.columns(2)
        with c1:
            # display contents of currently selected filter column
            filter_col = post.df[state.filter_col].drop_duplicates()
            st.selectbox("column filter value", filter_col.sort_values(), placeholder="None",
                         key="filter_val", index=None)
        with c2:
            st.text_input("custom filter value", None, placeholder="None", key="custom_filter_val",
                          help="{0} {1}".format("Assign a filter value that isn't in the data.",
                                                "Will cause column filter value to be ignored."))

        filter_val = state.custom_filter_val if state.custom_filter_val else state.filter_val
        current_filter = [state.filter_col, state.filter_op, filter_val]
        st.button("Add Filter", on_click=add_filter, args=[current_filter])


def update_filter(key: str):
    """
        Apply user-selected filters or series to session state config.

        Args:
            key: string, type of filter to update.
    """

    state = st.session_state
    config = state.config
    if key == "series":
        setattr(config, key, state[key])
    else:
        config.filters[key] = state[key]

    # re-parse filters
    config.parse_filters()
    # update types after changing filters or series
    update_types()


def add_filter(filter: list):
    """
        Allow the user to add a new filter or series to session state config.

        Args:
            filter: list, filter column, operator, and value.
    """

    state = st.session_state
    post = state.post
    key = state.filter_type

    if filter[-1] is not None:
        try:
            # type filter value as filter column type
            filter[-1] = post.val_as_dtype(filter[-1], dtype_lookup.get(state.filter_column_type)).iloc[0]
        except Exception as e:
            st.exception(e)
        # treat filter value as string
        filter[-1] = str(filter[-1])
        # remove operator from series
        if key == "series":
            del filter[1]

        if filter not in state[key]:
            try:
                # add filter to appropriate filter list
                state[key].append(filter)
                # update column type
                state.config.column_types[filter[0]] = state.filter_column_type
                # add filter to config and update df types
                update_filter(key)

                # (re-)interpret all filter values as given dtype of filter column
                # FIXME: should this be applied to all other filter lists too?
                for f in state[key]:
                    # found filter column matches current filter column
                    if f[0] == filter[0]:
                        # find filter index
                        i = state[key].index(f)
                        filter_value = post.val_as_col_dtype(state[key][i][-1], filter[0]).iloc[0]
                        # adjust filter value after typing
                        state[key][i][-1] = str(filter_value)

            except Exception as e:
                st.exception(e)
                post.plot = None
                # remove filter from filter list
                state[key].remove(filter)
                # re-update filter list
                update_filter(key)

        else:
            # warn if selected filter is already present
            st.warning("Currently selected filter is already present.")

    else:
        # warn if both column and custom filter values are blank
        st.warning("Currently selected filter cannot be added. Missing filter value information.")


def extra_columns():
    """
        Display current extra columns.
    """

    config = st.session_state.config
    st.write("###### Current Extra Columns")
    st.multiselect("Extra Columns", config.extra_columns if config.extra_columns else [None],
                   config.extra_columns, key="extra_columns", on_change=update_extra_column,
                   placeholder="None", label_visibility="collapsed")


def new_extra_column_options():
    """
        Display new extra column addition options interface.
    """

    state = st.session_state
    post = state.post
    with st.expander("Add New Extra Column"):

        st.selectbox("extra column", post.df.columns, key="extra_col",
                     help="{0} {1}".format(
                         "Optional columns to display in the filtered DataFrame (in addition to plot columns).",
                         "Extra columns do not affect plotting."))
        st.button("Add Extra Column", on_click=add_extra_column)


def update_extra_column():
    """
        Apply user-selected extra columns to session state config.
    """

    state = st.session_state
    config = state.config
    # align states
    config.extra_columns = state.extra_columns


def add_extra_column():
    """
        Allow the user to add a new extra column to session state config.
    """

    state = st.session_state
    config = state.config

    # warn if selected extra column is already present
    if (len(config.plot_columns + config.extra_columns + [state.extra_col]) !=
        len(set(config.plot_columns + config.extra_columns + [state.extra_col]))):
        st.warning("Currently selected extra column is already present in the DataFrame mask.")

    if state.extra_col not in state.config.extra_columns:
        # add extra column to list
        config.extra_columns.append(state.extra_col)
        # re-parse column names
        config.parse_columns()


def rerun_post_processing():
    """
        Run post-processing with the current session state config.
    """

    post = st.session_state.post
    config = st.session_state.config

    try:
        # validate config
        read_config(config.to_dict())
        # reset processed df to original state
        post.df = post.original_df.copy()
        # run post-processing again
        post.run_post_processing(config)

    except Exception as e:
        st.exception(e)
        post.plot = None


def validate_download_config():
    """
        Warn the user if the current session state config is invalid before download.
    """

    state = st.session_state
    try:
        # validate config
        read_config(state.config.to_dict())
    except Exception as e:
        st.warning("Download successful.\n\n" + type(e).__name__ + ": " + str(e))
        state.post.plot = None


def read_args():
    """
        Return parsed command line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Plot benchmark data. At least one perflog must be supplied.")

    # required positional argument (log path)
    parser.add_argument("log_path", type=Path,
                        help="path to a perflog file or a directory containing perflog files")
    # optional argument (config path)
    parser.add_argument("-c", "--config_path", type=Path, default=None,
                        help="path to a configuration file specifying what to plot")

    return parser.parse_args()


def main():

    args = read_args()

    try:
        post = PostProcessing(args.log_path)
        # set up empty template config
        config, err = ConfigHandler.from_template(), None
        # optionally load config from file path
        if args.config_path:
            try:
                config = ConfigHandler.from_path(args.config_path)
                # only run post-processing with a valid config
                post.run_post_processing(config)
            except Exception as e:
                err = e
                # autofill some information from invalid config
                try:
                    config = ConfigHandler.from_path(args.config_path, template=True)
                except Exception as e:
                    print(type(e).__name__ + ":", e)
                    print(traceback.format_exc())

        # display ui
        update_ui(post, config, e=err)

    except Exception as e:
        st.exception(e)
        print(type(e).__name__ + ":", e)
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
