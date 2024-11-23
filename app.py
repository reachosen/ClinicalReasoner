import streamlit as st
from stages.stage_select_scenario import run as stage_select_scenario
from stages.stage_select_patient import run as stage_select_patient
from stages.stage_generate_json import run as stage_generate_json
from stages.stage_choose_lens import run as stage_choose_lens
from stages.stage_patient_summary import run as stage_patient_summary
from stages.stage_generate_reasoning_chains import run as stage_generate_reasoning_chains
from stages.stage_generate_propositions import run as stage_generate_propositions
from stages.stage_validate_propositions import run as stage_validate_propositions
from stages.stage_proposition_driven_reasoning_chains import run as stage_proposition_driven_reasoning_chains
from stages.stage_validate import run as stage_validate
from stages.stage_brainstorm import run as stage_brainstorm

from components.session_utils import initialize_session_state, reset_session_state, display_stage_navigation_with_progress, go_to_previous_stage, go_to_next_stage, is_current_stage_completed
from components.stage_template import stage_template

# Initialize session state
initialize_session_state()

# Define stages
stages = [
    "Select Scenario",
    "Select Patient",
    "Generate JSON",
    "Choose Lens",
    "Patient Summary",
    "Generate Reasoning Chains",
    "Generate Propositions",
    "Validate Propositions",
    "Proposition-Driven Reasoning Chains",
    "Validate Reasoning Chains",
    "Brainstorm"
]

# Apply the template to stages that don't have their own navigation
stages_dict = {
    "Select Scenario": stage_select_scenario,
    "Select Patient": stage_select_patient,
    "Generate JSON": stage_generate_json,
    "Choose Lens": stage_choose_lens,
    "Patient Summary": stage_patient_summary,  # Remove the stage_template wrapper
    "Generate Reasoning Chains": stage_generate_reasoning_chains,
    "Generate Propositions": stage_template(stage_generate_propositions),
    "Validate Propositions": stage_template(stage_validate_propositions),
    "Proposition-Driven Reasoning Chains": stage_template(stage_proposition_driven_reasoning_chains),
    "Validate Reasoning Chains": stage_validate,
    "Brainstorm": stage_brainstorm
}

# Display the combined stage navigation and progress in the sidebar
display_stage_navigation_with_progress(stages)

# Auto-Selection Mode
st.sidebar.markdown("## Auto-Selection Mode")
st.sidebar.markdown("Auto-selection randomly chooses options in applicable stages. Use the toggle in each relevant stage to enable or disable.")

# Run the current stage
stage_name = stages[st.session_state.stage_index]
stages_dict[stage_name]()

# Centralized navigation
col1, col2 = st.columns([1, 1])
with col1:
    if st.session_state.stage_index > 0:
        if st.button("Back"):
            go_to_previous_stage()
            st.experimental_rerun()
with col2:
    if st.session_state.stage_index < len(stages) - 1:
        if st.button("Next"):
            if is_current_stage_completed():
                go_to_next_stage()
                st.experimental_rerun()
            else:
                st.warning("Please complete the current stage before proceeding.")

# Display reset button
st.sidebar.markdown("---")
if st.sidebar.button("Reset All Data"):
    reset_session_state()
    st.experimental_rerun()

# Do not add any navigation buttons here
