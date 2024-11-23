import streamlit as st
import random
from components.session_utils import mark_stage_as_completed

def run():
    st.title("Choose Lens")

    if 'patient_json_data' in st.session_state:
        chunked_data = st.session_state['patient_json_data']
        st.write(f"Patient data loaded: {len(chunked_data)} chunks")

        # Define lenses options
        lenses = ["Reducing Cost of Readmissions", "Improving Patient Satisfaction", "Enhancing Care Efficiency"]
        
        # Auto-selection explanation and button
        st.markdown("### Auto-Selection Mode")
        st.markdown("Automatically selects 1-3 random lenses.")
        auto_select = st.button("Use Auto-Selection")

        if auto_select:
            # Randomly select 1-3 lenses
            selected_lenses = random.sample(lenses, random.randint(1, 3))
            st.success(f"Auto-selected lenses: {', '.join(selected_lenses)}")
        else:
            # Manual selection
            selected_lenses = st.multiselect("Select Lenses", lenses, default=lenses[0])

        # Update session state with the selected lenses
        st.session_state.summary['Lenses'] = selected_lenses
        st.session_state['lens'] = selected_lenses

        if selected_lenses:
            st.success(f"Selected lenses: {', '.join(selected_lenses)}")
            mark_stage_as_completed()
        else:
            st.warning("Please select at least one lens.")

    else:
        st.error("No patient data loaded. Please go back and generate patient JSON first.")

    # Display the current state of stage completion
    st.write(f"Stage completed: {st.session_state.stage_completed[st.session_state.stage_index]}")
