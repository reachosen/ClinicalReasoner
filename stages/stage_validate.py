import streamlit as st
from components.api_utils import validate_reasoning_chain
from components.session_utils import go_to_previous_stage, go_to_next_stage
from components.data_utils import get_relevant_patient_data, get_clinical_guidelines
import json
import plotly.graph_objs as go
import pandas as pd

# Define a high-contrast color palette
COLOR_PALETTE = {
    "background": "#FFFFFF",
    "text": "#000000",
    "primary": "#0066CC",
    "secondary": "#FF6600",
    "accent": "#009933",
}

def set_page_style():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {COLOR_PALETTE["background"]};
            color: {COLOR_PALETTE["text"]};
        }}
        .stButton>button {{
            color: {COLOR_PALETTE["background"]};
            background-color: {COLOR_PALETTE["primary"]};
            border: 2px solid {COLOR_PALETTE["primary"]};
        }}
        .stButton>button:hover {{
            background-color: {COLOR_PALETTE["secondary"]};
            border-color: {COLOR_PALETTE["secondary"]};
        }}
        h1, h2, h3 {{
            color: {COLOR_PALETTE["primary"]};
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def extract_relevant_data(patient_summary, progress_summary, reasoning_chain):
    relevant_data = {}
    all_data = {**patient_summary, **progress_summary}
    
    for key, value in all_data.items():
        if isinstance(value, str) and value.lower() in reasoning_chain.lower():
            relevant_data[key] = value
        elif isinstance(value, (int, float)) and str(value) in reasoning_chain:
            relevant_data[key] = value
    
    return relevant_data

def display_reasoning_chain_with_data(chain, patient_summary, progress_summary):
    if isinstance(chain, dict):
        st.markdown(f"**Question:** {chain.get('question', 'Not provided')}")
        st.markdown("**Reasoning Chain:**")
        for step in chain.get('steps', []):
            st.markdown(f"- {step}")
            relevant_data = extract_relevant_data(patient_summary, progress_summary, step)
            if relevant_data:
                df = pd.DataFrame(list(relevant_data.items()), columns=['Attribute', 'Value'])
                st.dataframe(df)
    elif isinstance(chain, str):
        st.markdown("**Reasoning Chain:**")
        st.markdown(chain)
        relevant_data = extract_relevant_data(patient_summary, progress_summary, chain)
        if relevant_data:
            df = pd.DataFrame(list(relevant_data.items()), columns=['Attribute', 'Value'])
            st.dataframe(df)
    else:
        st.error(f"Unexpected chain format: {type(chain)}")

def display_validation_results(validation_results):
    for i, result in enumerate(validation_results, 1):
        st.subheader(f"Validation Result for Chain {i}")
        st.markdown(f"**Clinical Question:** {result.get('clinical_question', 'Not provided')}")
        st.markdown(f"**Reasoning Chain:**")
        st.markdown(result.get('reasoning_chain', 'Not provided'))
        st.markdown(f"**Validation Status:** {result.get('validation_status', 'Not provided')}")
        st.markdown(f"**Recommendation:** {result.get('recommendation', 'Not provided')}")

        # Display interactive visualization
        fig = go.Figure(data=[go.Sankey(
            node = dict(
              pad = 15,
              thickness = 20,
              line = dict(color = COLOR_PALETTE["text"], width = 0.5),
              label = ["Patient Data", "Clinical Guidelines", "Reasoning Chain", "Validation"],
              color = COLOR_PALETTE["primary"]
            ),
            link = dict(
              source = [0, 1, 2],
              target = [2, 2, 3],
              value = [1, 1, 1],
              color = COLOR_PALETTE["secondary"]
          ))])

        fig.update_layout(
            title_text="Reasoning Chain Validation Flow",
            font_size=14,
            plot_bgcolor=COLOR_PALETTE["background"],
            paper_bgcolor=COLOR_PALETTE["background"],
            font_color=COLOR_PALETTE["text"]
        )
        st.plotly_chart(fig)

        st.markdown("---")

def run():
    set_page_style()
    st.title("Validate Reasoning Chains")

    if 'reasoning_chains' in st.session_state and st.session_state['reasoning_chains']:
        patient_summary = st.session_state.get('patient_summary', {})
        progress_summary = st.session_state.get('progress_summary', {})
        selected_lenses = st.session_state.summary.get('Lenses', [])

        validation_results = []

        for i, chain in enumerate(st.session_state['reasoning_chains'], 1):
            st.subheader(f"Reasoning Chain {i}")
            
            display_reasoning_chain_with_data(chain, patient_summary, progress_summary)
            
            # User confirmation
            user_confirmation = st.radio(f"Is the reasoning chain for Chain {i} valid based on the input data?", 
                                         ("Yes", "No", "Needs Review"), key=f"confirm_{i}")
            
            if st.button(f"Validate Chain {i}", key=f"validate_{i}"):
                if isinstance(chain, dict):
                    question = chain.get('question', '')
                    reasoning = "\n".join(chain.get('steps', []))
                elif isinstance(chain, str):
                    question = "Not provided"
                    reasoning = chain
                else:
                    question = "Not provided"
                    reasoning = str(chain)
                
                relevant_data = get_relevant_patient_data(patient_summary, progress_summary, question)
                guidelines = get_clinical_guidelines(question, selected_lenses)
                
                # Format the chain for validation
                formatted_chain = f"Question: {question}\n\nReasoning Chain:\n\n{reasoning}\n\n{{{{source patient data used for validation: include col name , csv values}}}}"
                
                validation_result = validate_reasoning_chain(json.dumps(formatted_chain), json.dumps(relevant_data), json.dumps(guidelines))
                
                # Add user confirmation to validation result
                validation_result['user_confirmation'] = user_confirmation
                
                validation_results.append(validation_result)

            st.markdown("---")

        if validation_results:
            display_validation_results(validation_results)

    else:
        st.error("No reasoning chains to validate. Please go back and generate reasoning chains first.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Reasoning Chains"):
            go_to_previous_stage()
    with col2:
        if st.button("Next"):
            go_to_next_stage()