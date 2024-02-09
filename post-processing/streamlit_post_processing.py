import traceback

import streamlit as st
from config_handler import ConfigHandler
from post_processing import PostProcessing, read_args


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

    # display graph
    st.bokeh_chart(st.session_state.post.plot, use_container_width=True)

    # display dataframe data
    show_df = st.toggle("Show DataFrame")
    if show_df:
        st.dataframe(st.session_state.post.df[st.session_state.post.mask][config.plot_columns],
                     hide_index=True, use_container_width=True)

    st.divider()
    # set plot title
    title = st.text_input("#### Title", config.title)
    if title != config.title:
        config.title = title

    st.write("#### Axis Options")
    st.write("TODO")

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

    st.button("Generate Graph", on_click=rerun_post_processing, args=[config])


def rerun_post_processing(config: ConfigHandler):
    # reset processed df to original state
    # FIXME: make this reset a post-processing function
    st.session_state.post.df = st.session_state.post.original_df.copy()
    # run post-processing again
    st.session_state.post.run_post_processing(config)


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
