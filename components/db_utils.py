import sqlite3
import pandas as pd

def get_db_connection():
    return sqlite3.connect('Readmissionv2.db')

def execute_query(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def load_scenario_groups():
    conn = get_db_connection()
    try:
        groups = pd.read_sql('SELECT group_id, group_name FROM Scenario_Groups', conn)
    finally:
        conn.close()
    return groups

def load_scenarios(group_ids):
    conn = get_db_connection()
    try:
        placeholders = ', '.join('?' for _ in group_ids)
        query = f'''
            SELECT s.scenario_id, s.scenario_name, s.sql_query, sg.group_name 
            FROM Scenarios s
            JOIN Scenario_Groups sg ON s.group_id = sg.group_id
            WHERE s.group_id IN ({placeholders})
        '''
        scenarios = pd.read_sql(query, conn, params=group_ids)
    finally:
        conn.close()
    return scenarios

def load_patient_data(scenario_sql_query):
    conn = get_db_connection()
    try:
        patient_data = pd.read_sql(scenario_sql_query, conn)
    finally:
        conn.close()
    return patient_data
