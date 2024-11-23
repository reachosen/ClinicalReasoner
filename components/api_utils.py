import os
from openai import OpenAI
import streamlit as st
import json
from functools import lru_cache
from components.cache_utils import flexible_cache

# Securely access API key
os.environ["OPENAI_API_KEY"] = api_key = st.secrets["global"]["OPENAI_API_KEY"]

# Initialize the OpenAI client with API key
client = OpenAI(api_key=api_key)

@flexible_cache(backend='disk', ttl=3600)
def generate_clinical_questions(combined_summary, lenses):
    # Convert lenses to a tuple to make it hashable
    lenses = tuple(lenses) if isinstance(lenses, list) else lenses
    
    combined_summary_dict = json.loads(combined_summary)
    patient_summary = combined_summary_dict["Patient Summary"]
    progress_summary = combined_summary_dict["Progress Summary"]

    patient_summary_str = "\n".join([f"{key}: {value}" for key, value in patient_summary.items()])
    progress_summary_str = "\n".join([f"{key}: {value}" for key, value in progress_summary.items()])
    
    all_questions = []
    for lens in lenses:
        prompt = (
            f"Patient Summary:\n{patient_summary_str}\n"
            f"Progress Summary:\n{progress_summary_str}\n"
            f"Generate key clinical questions to assess the patient's risk of readmission through the lens of '{lens}'. "
            "Each question should be concise and focused on a specific aspect of the patient's condition or care."
        )
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a clinical decision support system designed to analyze complex patient data and generate key clinical questions "
                        f"with a focus on '{lens}'. Your task is to create focused, relevant questions that will help assess the patient's risk of readmission."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        questions = response.choices[0].message.content.split('\n')
        all_questions.extend(questions)
    return all_questions

@flexible_cache(backend='disk', ttl=3600)
def generate_reasoning_chain(question, relevant_data, guidelines, lenses):
    prompt = f"""
    Clinical Question: {question}
    Relevant Patient Data: {relevant_data}
    Clinical Guidelines: {guidelines}
    Lenses: {', '.join(lenses)}

    Generate a detailed reasoning chain to address the clinical question. 
    Consider the relevant patient data and clinical guidelines.
    Provide a step-by-step logical progression that leads to a conclusion or recommendation.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a clinical decision support system designed to generate detailed reasoning chains based on clinical questions, patient data, and guidelines."
            },
            {"role": "user", "content": prompt}
        ]
    )

    reasoning_chain = response.choices[0].message.content.split('\n')
    return {
        'question': question,
        'steps': reasoning_chain
    }

@flexible_cache(backend='disk', ttl=3600)
def validate_reasoning_chain(chain, patient_summary, progress_summary):
    prompt = f"""
    Validate the following reasoning chain:

    Reasoning Chain:
    {chain}

    Patient Summary:
    {patient_summary}

    Progress Summary:
    {progress_summary}

    Provide:
    1. The clinical question this reasoning chain addresses
    2. Validation points (including references to patient data and clinical guidelines)
    3. Validation status (Validated, Needs Review, or Rejected)
    4. A final recommendation based on the validated reasoning chain

    Format your response as follows:
    Clinical Question: [Your answer here]
    Validation Points: [Your answer here]
    Validation Status: [Your answer here]
    Recommendation: [Your answer here]
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a clinical decision support system designed to validate reasoning chains based on patient data and medical knowledge."
            },
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content
    
    # Parse the response
    lines = content.split('\n')
    result = {
        'clinical_question': 'Not provided',
        'validation_points': 'Not provided',
        'validation_status': 'Not provided',
        'recommendation': 'Not provided'
    }
    current_key = None
    for line in lines:
        if line.startswith('Clinical Question:'):
            current_key = 'clinical_question'
            result[current_key] = line.split(':', 1)[1].strip()
        elif line.startswith('Validation Points:'):
            current_key = 'validation_points'
            result[current_key] = line.split(':', 1)[1].strip()
        elif line.startswith('Validation Status:'):
            current_key = 'validation_status'
            result[current_key] = line.split(':', 1)[1].strip()
        elif line.startswith('Recommendation:'):
            current_key = 'recommendation'
            result[current_key] = line.split(':', 1)[1].strip()
        elif current_key and line.strip():
            result[current_key] += ' ' + line.strip()

    return result

@lru_cache(maxsize=32)
def generate_propositions(prompt):
    """
    Generate propositions based on the given prompt using the OpenAI API.

    Args:
    prompt (str): The prompt to generate propositions from.

    Returns:
    list: A list of generated propositions.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a clinical decision support system designed to generate concise, actionable propositions based on patient data and clinical scenarios."
            },
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the generated propositions from the API response
    propositions = response.choices[0].message.content.split('\n')
    
    # Clean up the propositions (remove empty lines and numbering)
    propositions = [prop.strip() for prop in propositions if prop.strip()]
    propositions = [prop[prop.find('.') + 1:].strip() if prop[0].isdigit() else prop for prop in propositions]

    return propositions

