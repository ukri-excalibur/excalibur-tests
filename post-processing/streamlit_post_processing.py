import traceback

import streamlit as st
from config_handler import ConfigHandler, load_config
from post_processing import PostProcessing, read_args

# drop-down lists
column_types = ["datetime", "int", "float", "str"]
# user vs internal pandas type conversion
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
    st.write("TODO")

    # FIXME: try to make a custom tag-like component for filters and series
    # instead of using multiselect
    st.write("###### Current AND Filters")
    st.multiselect("AND Filters", config.and_filters if config.and_filters else [None], config.and_filters,
                   placeholder="None", label_visibility="collapsed", disabled=True)

    st.write("###### Current OR Filters")
    st.multiselect("OR Filters", config.or_filters if config.or_filters else [None], config.or_filters,
                   placeholder="None", label_visibility="collapsed", disabled=True)

    st.write("###### Current Series")
    st.multiselect("Series", config.series if config.series else [None], config.series,
                   placeholder="None", label_visibility="collapsed", disabled=True)

    generate_graph, download_config = st.columns(2)
    with generate_graph:
        st.button("Generate Graph", on_click=rerun_post_processing, use_container_width=True)
    with download_config:
        st.download_button("Download Config", config.to_yaml(),
                           "{0}_config.yaml".format((config.title).lower().replace(" ", "_")),
                           use_container_width=True)


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

    # FIXME: if both axis or unit columns are the same, this results in incorrect behaviour
    config = st.session_state.config
    x_column = st.session_state.x_axis_column
    y_column = st.session_state.y_axis_column
    x_units_column = st.session_state.x_axis_units_column
    x_units_custom = st.session_state.x_axis_units_custom
    y_units_column = st.session_state.y_axis_units_column
    y_units_custom = st.session_state.y_axis_units_custom

    # remove axis column types that are no longer needed
    remove_axis_type(x_column, config.x_axis["value"], [y_column, y_units_column, x_units_column])
    if x_units_column or x_units_custom:
        remove_axis_type(x_units_column if not x_units_custom else None, config.x_axis["units"].get("column"),
                         [y_column, y_units_column, x_column])
    remove_axis_type(y_column, config.y_axis["value"], [x_column, x_units_column, y_units_column])
    if y_units_column or y_units_custom:
        remove_axis_type(y_units_column if not y_units_custom else None, config.y_axis["units"].get("column"),
                         [x_column, x_units_column, y_column])

    # update columns
    config.x_axis["value"] = x_column
    config.y_axis["value"] = y_column
    # update units
    # NOTE: units are automatically interpreted as strings for simplicity
    # FIXME: currently the only way to clear column selection is to add custom units
    # (custom units can easily be overwritten with None by leaving text input empty)
    config.x_axis["units"] = {"custom": x_units_custom}
    if not x_units_custom and x_units_column:
        config.x_axis["units"] = {"column": x_units_column}
        config.column_types[x_units_column] = "str"
    config.y_axis["units"] = {"custom": y_units_custom}
    if not y_units_custom and y_units_column:
        config.y_axis["units"] = {"column": y_units_column}
        config.column_types[y_units_column] = "str"

    # re-parse column names
    config.parse_columns()
    # update types
    config.column_types[x_column] = st.session_state.x_axis_type
    config.column_types[y_column] = st.session_state.y_axis_type


def remove_axis_type(new_column: str, old_column: str, other_axis_columns: list):
    """
        Remove an old axis column from the session state config column types dictionary if it is redundant.

        Args:
            new_column: str, new axis column name in session state selection.
            old_column: str, old axis column name in session state config.
            other_axis_columns: str list, the names of other axis columns to check against in session state selection.
    """

    config = st.session_state.config
    if old_column != new_column:
        # check the old column is not needed for the other axis, scaling, filters, or series
        is_redundant = old_column not in (other_axis_columns +
                                          ([config.scaling_column["name"]]
                                           if config.scaling_column is not None else []) +
                                          config.series_columns + config.filter_columns)
        if is_redundant:
            config.column_types.pop(old_column, None)


def update_config():
    """
        Change session state config to uploaded config file.
    """
    uploaded_config = st.session_state.uploaded_config
    if uploaded_config:
        st.session_state.config = ConfigHandler(load_config(uploaded_config))
        # need to re-run here to update dataframe types
        rerun_post_processing()


def rerun_post_processing():
    """
        Run post-processing with the current session state config.
    """

    post = st.session_state.post
    # reset processed df to original state
    # FIXME: make this reset a post-processing function
    post.df = post.original_df.copy()
    # run post-processing again
    post.run_post_processing(st.session_state.config)


def main():

    args = read_args()

    try:
        post = PostProcessing(args.log_path, args.debug, args.verbose)
        config = ConfigHandler.from_path(args.config_path)
        post.run_post_processing(config)
        update_ui(post, config)

    except Exception as e:
        print(type(e).__name__ + ":", e)
        print("Post-processing stopped")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
