import streamlit as st
import json
from components.session_utils import mark_stage_as_completed

class PropositionValidationModule:
    def __init__(self, patient_data, clinical_guidelines, feedback_system=None):
        self.patient_data = patient_data
        self.clinical_guidelines = clinical_guidelines
        self.feedback_system = feedback_system

    def validate_against_patient_data(self, proposition):
        if 'high glucose' in proposition.lower() and self.patient_data.get('lab_results', {}).get('high_glucose') == 0:
            return False, "Invalid: Patient does not have high glucose levels."
        if 'adherence program' in proposition.lower() and self.patient_data.get('medication_adherence') == 1:
            return False, "Invalid: Patient is adherent to their medication."
        return True, "Valid based on patient data."

    def validate_against_guidelines(self, proposition):
        if 'adjust insulin' in proposition.lower() and not self.clinical_guidelines.get('adjust insulin', False):
            return False, "Invalid: Proposition contradicts clinical guidelines for insulin adjustment."
        if 'adherence program' in proposition.lower() and not self.clinical_guidelines.get('adherence program', False):
            return False, "Invalid: Proposition contradicts guidelines for adherence programs."
        return True, "Valid based on clinical guidelines."

    def validate_with_feedback(self, proposition):
        if self.feedback_system:
            feedback_result = self.feedback_system(proposition)
            if feedback_result == "invalid":
                return False, "Invalid: External feedback indicates this proposition is incorrect."
            return True, "Valid: External feedback indicates proposition is sound."
        return True, "No feedback system applied."

    def validate_proposition(self, proposition):
        valid_data, data_message = self.validate_against_patient_data(proposition)
        if not valid_data:
            return False, data_message
        valid_guidelines, guideline_message = self.validate_against_guidelines(proposition)
        if not valid_guidelines:
            return False, guideline_message
        valid_feedback, feedback_message = self.validate_with_feedback(proposition)
        if not valid_feedback:
            return False, feedback_message
        return True, "Valid: Proposition is sound across all validation steps."

    def validate_all_propositions(self, propositions):
        validation_results = []
        for proposition in propositions:
            is_valid, validation_message = self.validate_proposition(proposition)
            validation_results.append({
                "proposition": proposition,
                "is_valid": is_valid,
                "validation_message": validation_message
            })
        return validation_results

def run():
    st.title("Validate Propositions")

    if 'propositions_json' in st.session_state and st.session_state['propositions_json']:
        propositions = json.loads(st.session_state['propositions_json'])
        patient_summary = st.session_state.get('patient_summary', {})
        progress_summary = st.session_state.get('progress_summary', {})

        # Combine patient_summary and progress_summary for a complete patient data set
        patient_data = {**patient_summary, **progress_summary}

        # For this example, we'll use a simple clinical guideline. In a real scenario, this would be more comprehensive.
        clinical_guidelines = {
            "adjust insulin": True,
            "adherence program": True
        }

        # Initialize the PropositionValidationModule
        validator = PropositionValidationModule(patient_data, clinical_guidelines)

        # Validate all propositions
        validation_results = validator.validate_all_propositions([prop['text'] for prop in propositions])

        st.subheader("Validation Results")
        for result in validation_results:
            st.write(f"Proposition: {result['proposition']}")
            st.write(f"Valid: {'Yes' if result['is_valid'] else 'No'}")
            st.write(f"Message: {result['validation_message']}")
            st.write("---")

        # Store validation results in session state
        st.session_state['validation_results'] = validation_results

        mark_stage_as_completed()
    else:
        st.error("No propositions found. Please complete the 'Generate Propositions' stage first.")

    st.write(f"Stage completed: {st.session_state.stage_completed[st.session_state.stage_index]}")