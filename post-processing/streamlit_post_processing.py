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

    # display graph
    st.bokeh_chart(post.plot, use_container_width=True)

    # display dataframe data
    show_df = st.toggle("Show DataFrame")
    if show_df:
        st.dataframe(post.df[post.mask][config.plot_columns], hide_index=True, use_container_width=True)


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
