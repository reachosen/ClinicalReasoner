import streamlit as st
from components.api_utils import generate_clinical_questions, generate_reasoning_chain
from components.session_utils import mark_stage_as_completed, go_to_next_stage
from components.data_utils import get_relevant_patient_data, get_clinical_guidelines
import json

def display_reasoning_chains(reasoning_chains):
    if not reasoning_chains:
        st.warning("No reasoning chains available.")
        return

    for i, chain in enumerate(reasoning_chains, 1):
        st.subheader(f"Reasoning Chain {i}")
        st.write(f"Clinical Question: {chain['question']}")
        for step in chain['steps']:
            st.write(f"- {step}")
        st.markdown("---")

def run():
    st.title("Generate Reasoning Chains")

    if 'patient_summary' in st.session_state and 'progress_summary' in st.session_state:
        patient_summary = st.session_state['patient_summary']
        progress_summary = st.session_state['progress_summary']
        selected_lenses = st.session_state.summary.get('Lenses', [])

        st.write(f"Selected lenses: {', '.join(selected_lenses)}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Generate Reasoning Chains"):
                st.info("Generating clinical questions and reasoning chains...")
                
                combined_summary = {
                    "Patient Summary": patient_summary,
                    "Progress Summary": progress_summary
                }
                
                combined_summary_json = json.dumps(combined_summary)
                
                clinical_questions = generate_clinical_questions(combined_summary_json, tuple(selected_lenses))
                
                reasoning_chains = []
                for question in clinical_questions:
                    relevant_data = get_relevant_patient_data(patient_summary, progress_summary, question)
                    guidelines = get_clinical_guidelines(question, tuple(selected_lenses))
                    chain = generate_reasoning_chain(question, relevant_data, guidelines, tuple(selected_lenses))
                    reasoning_chains.append(chain)
                
                st.session_state['reasoning_chains'] = reasoning_chains
                st.success("Reasoning chains generated. Displaying results:")
                
                mark_stage_as_completed()
                
                display_reasoning_chains(reasoning_chains)

        with col2:
            if st.button("Skip Reasoning Chains"):
                st.warning("Skipping reasoning chain generation.")
                st.session_state['reasoning_chains'] = []
                mark_stage_as_completed()
                go_to_next_stage()

        if 'reasoning_chains' in st.session_state and st.session_state['reasoning_chains']:
            st.success("Reasoning chains already generated. Displaying results:")
            display_reasoning_chains(st.session_state['reasoning_chains'])

    else:
        st.error("No patient summary available. Please go back and complete the Patient Summary step.")