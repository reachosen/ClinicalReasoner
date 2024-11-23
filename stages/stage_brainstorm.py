import streamlit as st
from components.session_utils import (
    initialize_session_state, update_session_state_and_rerun, 
    display_session_state, reset_session_state, go_to_previous_stage, 
    go_to_next_stage, display_stage_navigation_with_progress
)
from config import stages  

def run():
    st.title("Brainstorm")
    # Display progress, current session state, and provide reset option
    # display_progress()
    # display_session_state()
    # reset_session_state()
    if 'patient_json_data' in st.session_state and 'selected_lenses' in st.session_state:
        st.write("Brainstorming session based on selected lenses and patient data.")
        # Add further functionality for brainstorming based on the data
    else:
        st.error("Please complete the previous stages before brainstorming.")
    
    if st.button("Next"):
        st.success("You have completed all stages.")
