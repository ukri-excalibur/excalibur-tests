import argparse
import traceback
from pathlib import Path

import streamlit as st
from config_handler import ConfigHandler, load_config, read_config
from post_processing import PostProcessing

# drop-down lists
operators = ["==", "!=", "<", ">", "<=", ">="]
column_types = ["datetime", "int", "float", "str"]
filter_types = ["and", "or", "series"]
# internal pandas vs user type conversion
type_lookup = {"datetime64[ns]": "datetime",
               "float64": "float",
               "Int64": "int",
               "object": "str"}


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
        st.bokeh_chart(post.plot, use_container_width=True)

    # display dataframe data
    show_df = st.toggle("Show DataFrame")
    if show_df:
        if len(config.plot_columns) > 0:
            st.dataframe(post.df[post.mask][config.plot_columns], hide_index=True, use_container_width=True)
        else:
            st.dataframe(post.df[post.mask], hide_index=True, use_container_width=True)

    # display config in current session state
    show_config = st.toggle("Show Config", key="show_config")
    if show_config:
        st.write(config.to_dict())

    # display config information
    with st.sidebar:

        # config file uploader
        st.file_uploader("Upload Config", type="yaml", key="uploaded_config", on_change=update_config)

        # set plot title
        title = st.text_input("#### Title", config.title, placeholder="None")
        if title != config.title:
            config.title = title

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
                                   use_container_width=True)
            else:
                st.button("Download Config", disabled=True, use_container_width=True)


def update_config():
    """
        Change session state config to uploaded config file.
    """

    state = st.session_state
    uploaded_config = state.uploaded_config
    if uploaded_config:

        try:
            state.config = ConfigHandler(load_config(uploaded_config))
            # update dataframe types
            state.post.apply_df_types(state.config.all_columns, state.config.column_types)

        except Exception as e:
            st.exception(e)
            state.post = None


def axis_options():
    """
        Display axis options interface.
    """

    config = st.session_state.config
    st.write("#### Axis Options")
    with st.form(key="axis_options"):

        # x-axis select
        axis_select("x", config.x_axis)
        sort = st.checkbox("sort descending", True if config.x_axis.get("sort") == "descending" else False)
        # y-axis select
        axis_select("y", config.y_axis)
        submit = st.form_submit_button("Update Axes")

        if submit:
            update_axes()
            config.x_axis["sort"] = "descending" if sort else "ascending"


def axis_select(label: str, axis: dict):
    """
        Allow the user to select axis column and type for post-processing.

        Args:
            label: str, axis label (either 'x' or 'y').
            axis: dict, axis column and units from config.
    """

    df = st.session_state.post.df
    # default drop-down selections
    type_index = column_types.index(type_lookup.get(str(df[axis["value"]].dtype))) if axis["value"] else 0
    column_index = list(df.columns).index(axis["value"]) if axis["value"] in df.columns else None

    # axis information drop-downs
    axis_type, axis_column = st.columns(2)
    # type select
    with axis_type:
        st.selectbox("{0}-axis type".format(label), column_types,
                     key="{0}_axis_type".format(label), index=type_index)
    # column select
    with axis_column:
        st.selectbox("{0}-axis column".format(label), df.columns,
                     key="{0}_axis_column".format(label), index=column_index)
    # units select
    units_select(label, axis)


def units_select(label: str, axis: dict):
    """
        Allow the user to select or specify axis units for post-processing.

        Args:
            label: str, axis label (either 'x' or 'y').
            axis: dict, axis column and units from config.
    """

    df = st.session_state.post.df
    # default drop-down selection
    units_index = list(df.columns).index(axis["units"]["column"]) if axis["units"].get("column") else None

    units_column, units_custom = st.columns(2)
    # units select
    with units_column:
        # NOTE: initialising with index=None allows value to be cleared, but doesn't allow a default value
        st.selectbox("{0}-axis units column".format(label), df.columns, placeholder="None",
                     key="{0}_axis_units_column".format(label), index=units_index)
    # set custom units
    with units_custom:
        st.text_input("{0}-axis units custom".format(label), axis["units"].get("custom"),
                      placeholder="None", key="{0}_axis_units_custom".format(label))


def update_axes():
    """
        Apply user-selected axis columns and types to session state config.
    """

    # FIXME (issue #271): if both axis columns are the same, this results in incorrect behaviour
    state = st.session_state
    config = state.config
    x_column = state.x_axis_column
    y_column = state.y_axis_column
    x_units_column = state.x_axis_units_column
    x_units_custom = state.x_axis_units_custom
    y_units_column = state.y_axis_units_column
    y_units_custom = state.y_axis_units_custom

    # update columns
    config.x_axis["value"] = x_column
    config.y_axis["value"] = y_column
    # update column types
    config.column_types[x_column] = state.x_axis_type
    config.column_types[y_column] = state.y_axis_type

    # update units
    # NOTE: units are automatically interpreted as strings for simplicity
    # FIXME (part of issue #268): currently the only way to clear column selection is to add custom units
    # (custom units can easily be overwritten with None by leaving text input empty)
    config.x_axis["units"] = {"custom": x_units_custom}
    if not x_units_custom and x_units_column:
        config.x_axis["units"] = {"column": x_units_column}
        config.column_types[x_units_column] = "str"
    config.y_axis["units"] = {"custom": y_units_custom}
    if not y_units_custom and y_units_column:
        config.y_axis["units"] = {"column": y_units_column}
        config.column_types[y_units_column] = "str"

    # update types after changing axes
    update_types()


def update_types():
    """
        Apply user-selected types to session state config and dataframe.
    """

    post = st.session_state.post
    config = st.session_state.config

    # re-parse column names
    config.parse_columns()
    # remove redundant types from config
    config.remove_redundant_types()
    try:
        # update dataframe types
        post.apply_df_types(config.all_columns, config.column_types)
    except Exception as e:
        st.exception(e)


def filter_options():
    """
        Display filter options interface.
    """

    st.write("#### Filter Options")
    # FIXME: inherit max width can be too large for sidebar
    # allow wide multiselect labels
    st.markdown(
        """
        <style>
            .stMultiSelect [data-baseweb=select] span{
                max-width: inherit;
            }
        </style>""",
        unsafe_allow_html=True)

    # display current filters
    current_filters()
    # display new filter addition options
    new_filter_options()


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
    # FIXME: can/should this section be placed before displaying current filters by caching earlier components?
    st.write("###### Add New Filter")
    with st.container(border=True):

        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("filter type", filter_types, key="filter_type")
        with c2:
            st.selectbox("column type", column_types, key="column_type")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.selectbox("filter column", post.df.columns, key="filter_col")
        with c2:
            if state.filter_type == "series":
                st.selectbox("operator", ["=="], key="filter_op")
            else:
                st.selectbox("operator", operators, key="filter_op")
        # FIXME: user should be allowed to select values that aren't in the column as well
        with c3:
            filter_col = post.df[state.filter_col].drop_duplicates()
            st.selectbox("filter value", filter_col.sort_values(), key="filter_val")

        current_filter = [state.filter_col, state.filter_op, state.filter_val]
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
    key = state.filter_type

    # remove operator from series
    if key == "series":
        del filter[1]

    if filter not in state[key]:
        # add filter to appropriate filter list
        state[key].append(filter)
        # update column type
        state.config.column_types[filter[0]] = state.column_type
        # add filter to config and update df types
        update_filter(key)
        # interpret filter value as filter column dtype
        filter_value = state.post.val_as_col_dtype(state[key][-1][-1], filter[0]).iloc[0]
        # adjust filter value after typing
        state[key][-1][-1] = str(filter_value)


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
        # display ui
        update_ui(post, config, e=err)

    except Exception as e:
        st.exception(e)
        print(type(e).__name__ + ":", e)
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
