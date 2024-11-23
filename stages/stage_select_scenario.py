import streamlit as st
import random
from components.db_utils import load_scenario_groups, load_scenarios
from components.session_utils import mark_stage_as_completed

def run():
    st.title("Select Scenario")

    # Load scenario groups
    scenario_groups = load_scenario_groups()
    
    # Auto-selection explanation and button
    st.markdown("### Auto-Selection Mode")
    st.markdown("Automatically selects a random scenario group and scenario.")
    auto_select = st.button("Use Auto-Selection")

    if auto_select:
        # Randomly select a scenario group and scenario
        selected_group = random.choice(scenario_groups['group_id'].tolist())
        scenarios = load_scenarios([selected_group])
        selected_scenario = random.choice(scenarios['scenario_id'].tolist())
        
        st.success(f"Auto-selected scenario: {scenarios[scenarios['scenario_id'] == selected_scenario]['scenario_name'].iloc[0]}")
    else:
        # Manual selection
        selected_group = st.selectbox(
            "Select a scenario group:",
            options=scenario_groups['group_id'].tolist(),
            format_func=lambda x: scenario_groups[scenario_groups['group_id'] == x]['group_name'].iloc[0]
        )

        if selected_group:
            scenarios = load_scenarios([selected_group])
            selected_scenario = st.selectbox(
                "Select a scenario:",
                options=scenarios['scenario_id'].tolist(),
                format_func=lambda x: scenarios[scenarios['scenario_id'] == x]['scenario_name'].iloc[0]
            )

    if selected_scenario:
        # Store the selected scenario in session state
        st.session_state.selected_scenario = selected_scenario
        st.session_state.scenario_sql_query = scenarios[scenarios['scenario_id'] == selected_scenario]['sql_query'].iloc[0]
        st.session_state.scenario_group = scenarios[scenarios['scenario_id'] == selected_scenario]['group_name'].iloc[0]
        st.session_state.scenario = scenarios[scenarios['scenario_id'] == selected_scenario]['scenario_name'].iloc[0]
        
        mark_stage_as_completed()

    # Display the current state of stage completion
    st.write(f"Stage completed: {st.session_state.stage_completed[st.session_state.stage_index]}")
