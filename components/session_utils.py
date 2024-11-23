import streamlit as st
from config import stages  # Ensure config imports stages list

def initialize_session_state():
    if 'stage_index' not in st.session_state:
        st.session_state.stage_index = 0
    if 'stage_completed' not in st.session_state:
        st.session_state.stage_completed = [False] * len(stages)
    if 'selected_scenario' not in st.session_state:
        st.session_state.selected_scenario = None
    if 'scenario_sql_query' not in st.session_state:
        st.session_state.scenario_sql_query = None
    if 'patient_selected' not in st.session_state:
        st.session_state.patient_selected = False
    if 'summary' not in st.session_state:
        st.session_state.summary = {}
    if 'patient_json_data' not in st.session_state:
        st.session_state.patient_json_data = None
    if 'reasoning_chains' not in st.session_state:
        st.session_state.reasoning_chains = []
    if 'chain_to_validate' not in st.session_state:
        st.session_state.chain_to_validate = None
    if 'propositions' not in st.session_state:
        st.session_state.propositions = None
    if 'proposition_driven_chains' not in st.session_state:
        st.session_state.proposition_driven_chains = None
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None

def update_session_state_and_rerun(key, value):
    st.session_state[key] = value
    st.experimental_rerun()

def display_session_state():
    """Display the current session state in the sidebar."""
    st.sidebar.markdown("### Current Session State")
    for key, value in st.session_state.items():
        st.sidebar.write(f"**{key}:** {value}")

def reset_session_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()

def go_to_previous_stage():
    """Move to the previous stage."""
    if st.session_state.stage_index > 0:
        st.session_state.stage_index -= 1

def go_to_next_stage():
    """Move to the next stage."""
    if st.session_state.stage_index < len(stages) - 1:
        st.session_state.stage_index += 1

def mark_stage_as_completed():
    st.session_state.stage_completed[st.session_state.stage_index] = True

def is_current_stage_completed():
    return st.session_state.stage_completed[st.session_state.stage_index]

def display_stage_navigation_with_progress(stages):
    """Display the combined stage navigation and progress in the sidebar."""
    st.sidebar.markdown("### Stage Navigation")
    for i, stage in enumerate(stages):
        if i < st.session_state.stage_index:
            st.sidebar.write(f"✅ {stage}")
        elif i == st.session_state.stage_index:
            st.sidebar.write(f"🔴 **{stage}**")  # Highlight current stage
        else:
            st.sidebar.write(f"⬜ {stage}")
