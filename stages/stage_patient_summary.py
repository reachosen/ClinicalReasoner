import streamlit as st
from components.session_utils import mark_stage_as_completed
import pandas as pd

def generate_patient_progress_summary(chunked_data):
    df = pd.DataFrame([item for sublist in chunked_data for item in sublist])
    df = df.sort_values('encounter_id')
    
    progress_columns = {
        'time_in_hospital': {'unit': 'days', 'improvement': 'decrease'},
        'num_lab_procedures': {'unit': 'count', 'improvement': 'context_dependent'},
        'num_procedures': {'unit': 'count', 'improvement': 'context_dependent'},
        'num_medications': {'unit': 'count', 'improvement': 'decrease'},
        'number_outpatient': {'unit': 'days', 'improvement': 'context_dependent'},
        'number_emergency': {'unit': 'days', 'improvement': 'decrease'},
        'number_inpatient': {'unit': 'days', 'improvement': 'decrease'},
        'diabetesMed': {'unit': 'N/A', 'improvement': 'context_dependent'},
        'A1Cresult': {'unit': '%', 'improvement': 'decrease'}
    }
    
    summary = {}
    key_insights = []
    
    for column, info in progress_columns.items():
        column_data = df[column]
        
        if pd.api.types.is_numeric_dtype(column_data):
            initial_value = float(column_data.iloc[0])
            final_value = float(column_data.iloc[-1])
            max_value = float(column_data.max())
            average_per_visit = float(column_data.mean())
            total_across_visits = float(column_data.sum())
            
            significant_change_threshold = 0.5 * average_per_visit
            
            significant_visits = [(i+1, val) for i, val in enumerate(column_data) if val > significant_change_threshold]
            
            if all(value == 0 for value in column_data):
                trend = 'Zero'
            elif final_value > initial_value:
                trend = 'Increasing'
            elif final_value < initial_value:
                trend = 'Decreasing'
            else:
                trend = 'Stable'
            
            if info['improvement'] == 'decrease':
                interpretation = 'Optimal' if trend == 'Zero' else trend
            elif info['improvement'] == 'increase':
                interpretation = 'Concern' if trend == 'Zero' else trend
            else:
                interpretation = trend
            
            if significant_visits:
                milestone_visit = ", ".join([f"Visit {v[0]}" for v in significant_visits])
                key_insights.append(f"{column}: {interpretation}. Significant: {milestone_visit}. "
                                    f"Initial: {initial_value}, Final: {final_value}, Max: {max_value}.")
            else:
                milestone_visit = 'None'
                key_insights.append(f"{column}: {interpretation}. "
                                    f"Initial: {initial_value}, Final: {final_value}, Max: {max_value}.")
        else:
            unique_values = column_data.unique()
            initial_value = str(column_data.iloc[0])
            max_value = 'N/A'
            average_per_visit = 'N/A'
            total_across_visits = 'N/A'
            
            changes = column_data != column_data.shift()
            milestone_visits = [f"Visit {i+1}" for i, change in enumerate(changes) if change]
            milestone_visit = ", ".join(milestone_visits) if milestone_visits else 'None'
            
            interpretation = 'Changed' if len(unique_values) > 1 else 'Stable'
            
            key_insights.append(f"{column}: {interpretation}. Initial: {initial_value}, Final: {column_data.iloc[-1]}.")
        
        atomic_data = ', '.join(map(str, column_data.tolist()))
        
        summary[column] = {
            'Initial Value': f"{initial_value} {info['unit']}",
            'Max Value': f"{max_value} {info['unit']}" if max_value != 'N/A' else max_value,
            'Interpretation': interpretation,
            'Significant Visits': milestone_visit,
            'Average per Visit': f"{average_per_visit:.1f} {info['unit']}" if average_per_visit != 'N/A' else average_per_visit,
            'Total Across Visits': f"{total_across_visits:.0f} {info['unit']}" if total_across_visits != 'N/A' else total_across_visits,
            'Atomic Data': atomic_data
        }
    
    return summary, len(df), key_insights

def create_patient_summary(chunked_data):
    all_data = [item for sublist in chunked_data for item in sublist]
    
    first_encounter = all_data[0]
    last_encounter = all_data[-1]
    
    summary = {
        "Patient ID": str(first_encounter['patient_nbr']),
        "Total Encounters": len(all_data),
        "First Encounter Date": str(first_encounter['encounter_id']),
        "Last Encounter Date": str(last_encounter['encounter_id']),
        "Age": str(first_encounter['age']),
        "Gender": first_encounter['gender'],
        "Race": first_encounter['race'],
        "Initial Diagnosis": first_encounter['diag_1'],
        "Final Diagnosis": last_encounter['diag_1'],
        "Medications": list(set([encounter['medical_specialty'] for encounter in all_data if encounter['medical_specialty'] != '?']))
    }
    
    return summary

def run():
    st.title("Patient Summary")

    if 'patient_json_data' in st.session_state and 'summary' in st.session_state:
        chunked_data = st.session_state['patient_json_data']
        selected_lenses = st.session_state.summary.get('Lenses', [])

        st.write(f"Patient data loaded: {len(chunked_data)} chunks")
        st.write(f"Selected lenses: {', '.join(selected_lenses)}")

        progress_summary, total_visits, key_insights = generate_patient_progress_summary(chunked_data)
        st.subheader(f"Patient Progress Across {total_visits} Visits")
        
        st.subheader("Key Insights")
        for insight in key_insights:
            st.markdown(f"- {insight}")
        
        st.subheader("Patient Progress Summary")
        
        matrix_data = []
        headers = ['Metric', 'Initial Value', 'Max Value', 'Interpretation', 'Significant Visits', 'Average per Visit', 'Total Across Visits', 'Atomic Data']
        matrix_data.append(headers)
        
        for metric, data in progress_summary.items():
            row = [
                metric,
                data['Initial Value'],
                data['Max Value'],
                data['Interpretation'],
                data['Significant Visits'],
                data['Average per Visit'],
                data['Total Across Visits'],
                data['Atomic Data']
            ]
            matrix_data.append(row)
        
        st.table(matrix_data)

        patient_summary = create_patient_summary(chunked_data)
        st.session_state['patient_summary'] = patient_summary
        st.session_state['progress_summary'] = progress_summary

        # Mark this stage as completed
        mark_stage_as_completed()
    else:
        st.error("No patient data or lenses selected. Please go back and complete previous steps.")

    # Display the current state of stage completion
    st.write(f"Stage completed: {st.session_state.stage_completed[st.session_state.stage_index]}")