import json

def chunk_json(data, chunk_size=5):
    """
    Chunks a list of dictionaries into smaller lists.
    
    Args:
    data (list): List of dictionaries to be chunked.
    chunk_size (int): Number of items per chunk.
    
    Returns:
    list: List of chunked data.
    """
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def get_relevant_patient_data(patient_summary, progress_summary, question):
    # Implement logic to extract relevant patient data based on the question
    # This is a placeholder implementation
    return f"Relevant data for question: {question}"

def get_clinical_guidelines(question, lenses):
    # Implement logic to fetch relevant clinical guidelines based on the question and lenses
    # This is a placeholder implementation
    return f"Guidelines for question: {question} and lenses: {', '.join(lenses)}"