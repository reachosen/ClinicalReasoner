import streamlit as st
import pandas as pd
import json
from components.db_utils import get_db_connection
from components.session_utils import mark_stage_as_completed
from components.data_utils import chunk_json

def run():
    st.title("Generate Patient JSON")
    
    if 'patient_selected' in st.session_state and st.session_state.patient_selected:
        selected_patient_id = st.session_state.summary['Patient ID']

        conn = get_db_connection()
        try:
            # Query to get all encounters for the patient, ordered by sequence_number
            patient_data_query = f"""
                SELECT * FROM Diabetic_Data 
                WHERE patient_nbr = '{selected_patient_id}'
                ORDER BY sequence_number
            """
            patient_data = pd.read_sql(patient_data_query, conn)

            if not patient_data.empty:
                # Convert patient data to list of dictionaries
                patient_data_list = patient_data.to_dict('records')
                
                # Chunk the data
                chunked_data = list(chunk_json(patient_data_list))
                
                # Display chunked data
                for i, chunk in enumerate(chunked_data):
                    st.subheader(f"Chunk {i+1}")
                    st.json(json.dumps(chunk, indent=2))
                
                # Save the chunked JSON data to session state for later use
                st.session_state['patient_json_data'] = chunked_data
                st.success(f"Generated {len(chunked_data)} chunks of patient data.")

                # Mark this stage as completed
                mark_stage_as_completed()
            else:
                st.error("No data found for the provided patient ID.")
        
        finally:
            conn.close()
                
    else:
        st.error("No patient selected. Please go back and select a patient.")

    # Display the current state of stage completion
    st.write(f"Stage completed: {st.session_state.stage_completed[st.session_state.stage_index]}")
