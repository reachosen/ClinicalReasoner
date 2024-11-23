import streamlit as st
import json
from components.api_utils import generate_propositions
from components.session_utils import mark_stage_as_completed

def generate_propositions_prompt(scenario_group, scenario, patient_data, lens):
    """
    Generates a dynamic prompt based on the scenario group, scenario, patient data, and chosen lens for generating actionable propositions.
    
    Parameters:
    scenario_group (str): The broader scenario group selected (e.g., Medication Management, Emergency Care).
    scenario (str): The specific scenario selected within the group.
    patient_data (list): A list of lists containing patient encounter data.
    lens (list): A list of lenses selected for the reasoning chain (e.g., reducing costs, improving satisfaction).
    
    Returns:
    str: A dynamically generated prompt for generating concise, actionable propositions.
    """
    
    # Start with the scenario group, scenario, and lens
    prompt = f"Generate concise, actionable propositions for the scenario group '{scenario_group}' and scenario '{scenario}' considering the following lens: {', '.join(lens)}.\n\n"
    
    prompt += "Patient Data Summary:\n"
    
    # Loop through each chunk of encounters
    for chunk_index, chunk in enumerate(patient_data, start=1):
        prompt += f"\nPatient Encounters - Chunk {chunk_index}:\n"
        
        # Loop through each encounter within the chunk
        for encounter_index, encounter in enumerate(chunk, start=1):
            prompt += f"  Encounter {encounter_index}:\n"
            
            # Add relevant information if present in the encounter
            if 'medication_adherence' in encounter:
                adherence_status = 'Adherent' if encounter['medication_adherence'] == 1 else 'Non-Adherent'
                prompt += f"    - Medication Adherence: {adherence_status}\n"
                
            if 'hospital_visits' in encounter:
                emergency_visits = encounter['hospital_visits'].get('emergency_visits', 'N/A')
                inpatient_visits = encounter['hospital_visits'].get('inpatient_visits', 'N/A')
                prompt += f"    - Emergency Visits: {emergency_visits}\n"
                prompt += f"    - Inpatient Visits: {inpatient_visits}\n"
                
            if 'lab_results' in encounter:
                glucose_level = 'High' if encounter['lab_results'].get('high_glucose') == 1 else 'Normal'
                prompt += f"    - Glucose Levels: {glucose_level}\n"
                
            if 'readmitted' in encounter:
                readmission_status = 'Yes' if '<30' in encounter['readmitted'] else 'No'
                prompt += f"    - Readmitted within 30 days: {readmission_status}\n"

    # End the prompt with a clear call-to-action for generating propositions
    prompt += "\nBased on the summarized data, generate concise propositions for managing the patient's care with a focus on the selected lens.\n"
    
    return prompt



def display_propositions(propositions):
    """
    Displays the generated propositions in a clear and concise format.
    """
    if not propositions:
        st.warning("No propositions available.")
        return

    st.subheader("Generated Propositions")
    for i, proposition in enumerate(propositions, 1):
        st.write(f"{i}. {proposition}")


def run():
    st.title("Generate Propositions")

    if 'patient_json_data' in st.session_state and 'scenario_group' in st.session_state and 'scenario' in st.session_state and 'lens' in st.session_state:
        patient_data = st.session_state['patient_json_data']
        scenario_group = st.session_state['scenario_group']
        scenario = st.session_state['scenario']
        lens = st.session_state['lens']

        st.write(f"Scenario Group: {scenario_group}")
        st.write(f"Scenario: {scenario}")
        st.write(f"Selected Lens: {', '.join(lens)}")

        if 'propositions_json' not in st.session_state or not st.session_state['propositions_json']:
            if st.button("Generate Propositions"):
                st.info("Generating propositions based on patient data...")
                
                prompt = generate_propositions_prompt(scenario_group, scenario, patient_data, lens)
                propositions = generate_propositions(prompt)
                
                # Store propositions as JSON in session state
                propositions_json = json.dumps([{"id": i, "text": prop} for i, prop in enumerate(propositions)])
                st.session_state['propositions_json'] = propositions_json
                
                st.success("Propositions generated. Displaying results:")
                display_propositions(propositions)
                mark_stage_as_completed()
        else:
            st.success("Propositions already generated. Displaying results:")
            propositions = [prop["text"] for prop in json.loads(st.session_state['propositions_json'])]
            display_propositions(propositions)
            mark_stage_as_completed()

        if st.button("Regenerate Propositions"):
            st.session_state.pop('propositions_json', None)
            st.experimental_rerun()

    else:
        st.error("Missing required data. Please ensure you've completed the previous steps.")

    st.write(f"Stage completed: {st.session_state.stage_completed[st.session_state.stage_index]}")
