import traceback

import streamlit as st
from config_handler import ConfigHandler, load_config
from post_processing import PostProcessing, read_args

# drop-down lists
operators = ["==", "!=", "<", ">", "<=", ">="]
column_types = ["datetime", "int", "float", "str"]
filter_types = ["and", "or", "series"]
# internal pandas vs user type conversion
type_lookup = {"datetime64[ns]": "datetime",
               "float64": "float",
               "Int64": "int",
               "object": "str"}


def update_ui(post: PostProcessing, config: ConfigHandler):
    """
        Create an interactive user interface for post-processing using Streamlit.

        Args:
            post: PostProcessing, class containing performance log data and filter information.
            config: ConfigHandler, class containing configuration information for plotting.
    """

    # stop the session state from resetting each time this function is run
    if st.session_state.get("post") is None:
        st.session_state.post = post
        st.session_state.config = config

    post = st.session_state.post
    config = st.session_state.config

    # display graph
    st.bokeh_chart(post.plot, use_container_width=True)

    # display dataframe data
    show_df = st.toggle("Show DataFrame")
    if show_df:
        st.dataframe(post.df[post.mask][config.plot_columns], hide_index=True, use_container_width=True)

    st.divider()
    st.file_uploader("Upload Config", type="yaml", key="uploaded_config", on_change=update_config)

    # set plot title
    title = st.text_input("#### Title", config.title)
    if title != config.title:
        config.title = title

    st.write("#### Axis Options")
    with st.form(key="axis options"):
        axis_select("x", config.x_axis)
        sort = st.checkbox("sort descending", True if config.x_axis.get("sort") == "descending" else False)
        axis_select("y", config.y_axis)
        submit = st.form_submit_button("Update Axes")
        if submit:
            update_axes()
            config.x_axis["sort"] = "descending" if sort else "ascending"

    st.write("#### Filter Options")
    # allow wide multiselect labels
    st.markdown(
        """
        <style>
            .stMultiSelect [data-baseweb=select] span{
                max-width: inherit;
            }
        </style>""",
        unsafe_allow_html=True)

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

    # update types after changing axes, filters, and series
    update_types()

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
            if st.session_state.filter_type == "series":
                st.selectbox("operator", ["=="], key="filter_op")
            else:
                st.selectbox("operator", operators, key="filter_op")
        # FIXME: user should be allowed to select values that aren't in the column as well
        with c3:
            filter_col = post.df[st.session_state.filter_col].drop_duplicates()
            st.selectbox("filter value", filter_col.sort_values(), key="filter_val")

        current_filter = [st.session_state.filter_col,
                          st.session_state.filter_op,
                          st.session_state.filter_val]
        st.button("Add Filter", on_click=add_filter, args=[current_filter])

    generate_graph, download_config = st.columns(2)
    with generate_graph:
        st.button("Generate Graph", on_click=rerun_post_processing, use_container_width=True)
    with download_config:
        st.download_button("Download Config", config.to_yaml(),
                           "{0}_config.yaml".format((config.title).lower().replace(" ", "_")),
                           use_container_width=True)


def update_config():
    """
        Change session state config to uploaded config file.
    """

    uploaded_config = st.session_state.uploaded_config
    if uploaded_config:
        st.session_state.config = ConfigHandler(load_config(uploaded_config))


def axis_select(label: str, axis: dict):
    """
        Allow the user to select axis column and type for post-processing.

        Args:
            label: str, axis label (either 'x' or 'y').
            axis: dict, axis column and units from config.
    """

    df = st.session_state.post.df
    # default drop-down selections
    type_index = column_types.index(type_lookup.get(str(df[axis["value"]].dtype)))
    column_index = list(df.columns).index(axis["value"])

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
    config = st.session_state.config
    x_column = st.session_state.x_axis_column
    y_column = st.session_state.y_axis_column
    x_units_column = st.session_state.x_axis_units_column
    x_units_custom = st.session_state.x_axis_units_custom
    y_units_column = st.session_state.y_axis_units_column
    y_units_custom = st.session_state.y_axis_units_custom

    # update columns
    config.x_axis["value"] = x_column
    config.y_axis["value"] = y_column
    # update column types
    config.column_types[x_column] = st.session_state.x_axis_type
    config.column_types[y_column] = st.session_state.y_axis_type

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
    # update dataframe types
    post.apply_df_types(config.all_columns, config.column_types)


def update_filter(key):
    """
        Apply user-selected filters or series to session state config.

        Args:
            key: string, type of filter to update.
    """

    config = st.session_state.config
    if key == "series":
        setattr(config, key, st.session_state[key])
    else:
        config.filters[key] = st.session_state[key]
    # re-parse filters
    config.parse_filters()


def add_filter(filter):
    """
        Allow the user to add a new filter or series to session state config.

        Args:
            filter: list, filter column, operator, and value.
    """

    # FIXME: there is a problem with filter datetime/timestamp formatting that requires further investigation
    key = st.session_state.filter_type
    loc = st.session_state[key]
    if filter not in loc:
        # remove operator from series
        if key == "series":
            del filter[1]
        # add filter to appropriate list location and config
        loc.append(filter)
        update_filter(key)
        # update column type
        st.session_state.config.column_types[filter[0]] = st.session_state.column_type


def rerun_post_processing():
    """
        Run post-processing with the current session state config.
    """

    post = st.session_state.post
    # reset processed df to original state
    post.df = post.original_df.copy()
    # run post-processing again
    post.run_post_processing(st.session_state.config)


def main():

    args = read_args()

    try:
        post = PostProcessing(args.log_path, args.debug, args.verbose)
        config = ConfigHandler.from_path(args.config_path)
        post.run_post_processing(config)
        # FIXME (#issue #271): catch post-processing errors before they crash Streamlit
        update_ui(post, config)

    except Exception as e:
        print(type(e).__name__ + ":", e)
        print("Post-processing stopped")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
