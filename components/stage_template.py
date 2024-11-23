import streamlit as st
from components.session_utils import go_to_previous_stage, go_to_next_stage

def stage_template(content_function):
    def wrapper():
        content_function()

        # Only add navigation if it's not already present
        if 'navigation_added' not in st.session_state:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("Back", key="back_button_generic"):
                    go_to_previous_stage()
            with col3:
                if st.button("Next", key="next_button_generic"):
                    go_to_next_stage()
            st.session_state.navigation_added = True

    return wrapper