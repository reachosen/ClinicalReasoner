import streamlit as st
import json
from components.api_utils import generate_reasoning_chain
from components.session_utils import mark_stage_as_completed

def run():
    st.title("Proposition-Driven Reasoning Chains")

    if 'propositions_json' in st.session_state and st.session_state['propositions_json']:
        propositions = json.loads(st.session_state['propositions_json'])
        patient_summary = st.session_state.get('patient_summary', {})
        progress_summary = st.session_state.get('progress_summary', {})

        st.write("Generated Propositions:")
        for prop in propositions:
            st.write(f"{prop['id'] + 1}. {prop['text']}")

        st.write("\nGenerating reasoning chains based on these propositions...")

        proposition_driven_chains = []

        for prop in propositions:
            # Combine patient_summary and progress_summary for a complete patient data set
            patient_data = {**patient_summary, **progress_summary}
            chain = generate_reasoning_chain(prop['text'], patient_data)
            proposition_driven_chains.append({"proposition": prop['text'], "chain": chain})

        st.session_state['proposition_driven_chains'] = proposition_driven_chains

        st.subheader("Proposition-Driven Reasoning Chains")
        for i, item in enumerate(proposition_driven_chains, 1):
            st.write(f"Chain {i} (based on proposition: {item['proposition']})")
            st.write(item['chain'])
            st.write("---")

        mark_stage_as_completed()

    else:
        st.error("No propositions found. Please complete the 'Generate Propositions' stage first.")

    # Display the current state of stage completion
    st.write(f"Stage completed: {st.session_state.stage_completed[st.session_state.stage_index]}")