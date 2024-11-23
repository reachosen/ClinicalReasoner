import streamlit as st
import pandas as pd
from components.db_utils import get_db_connection, load_patient_data
from components.session_utils import (
    initialize_session_state, update_session_state_and_rerun, 
    display_session_state, reset_session_state, mark_stage_as_completed
)
from config import stages

def run():
    st.title("Select Patient")

    conn = get_db_connection()
    try:
        # Query to get patient IDs and visit counts, ordered by visit count descending
        query = """
            SELECT patient_nbr, COUNT(*) as visit_count
            FROM Diabetic_Data
            GROUP BY patient_nbr
            ORDER BY visit_count DESC
        """
        patient_data = pd.read_sql(query, conn)

        # Create visit count range filter
        visit_ranges = ["0-5 visits", "6-10 visits", "11-20 visits", ">20 visits"]
        selected_range = st.selectbox("Filter by visit count:", visit_ranges)

        # Filter patient data based on selected range
        if selected_range == "0-5 visits":
            filtered_data = patient_data[(patient_data['visit_count'] >= 0) & (patient_data['visit_count'] <= 5)]
        elif selected_range == "6-10 visits":
            filtered_data = patient_data[(patient_data['visit_count'] >= 6) & (patient_data['visit_count'] <= 10)]
        elif selected_range == "11-20 visits":
            filtered_data = patient_data[(patient_data['visit_count'] >= 11) & (patient_data['visit_count'] <= 20)]
        else:  # >20 visits
            filtered_data = patient_data[patient_data['visit_count'] > 20]

        # Create options for dropdown
        options = [f"{row['patient_nbr']} ({row['visit_count']} visits)" for _, row in filtered_data.iterrows()]
        
        selected_option = st.selectbox("Select a patient:", options)

        if selected_option:
            patient_id = selected_option.split()[0]  # Extract patient ID from the selected option
            visit_count = int(selected_option.split('(')[1].split()[0])  # Extract visit count

            st.session_state.summary = {
                "Patient ID": patient_id,
                "Visit Count": visit_count
            }
            st.session_state.patient_selected = True

            st.success(f"Selected Patient ID: {patient_id} with {visit_count} visits")

            # Display some sample data for the selected patient
            sample_data_query = f"""
                SELECT * FROM Diabetic_Data
                WHERE patient_nbr = '{patient_id}'
                LIMIT 5
            """
            sample_data = pd.read_sql(sample_data_query, conn)
            st.subheader("Sample Data for Selected Patient")
            st.dataframe(sample_data)

            # Mark this stage as completed
            mark_stage_as_completed()

    finally:
        conn.close()

    # Display the current state of stage completion
    st.write(f"Stage completed: {st.session_state.stage_completed[st.session_state.stage_index]}")
