import re
from supabase import create_client, Client
import streamlit as st

def create_options(Name: str, x_ID: str):
    return Name + " (ID: " + str(x_ID) + ")"

def get_ID(selected):
    selected = re.findall(r'\d+', selected)
    return int(selected[0])

def create_edit_injury_options(data):
    row_labels = []

    for row in data:
        row_labels.append(f"{row['InjuryStartDate']} / {row['Player']['PlayerName']} / {row['OSIICS']['OSIICS_Diagnosis']}")
    
    return row_labels

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def run_query(QueryName: str):

    if QueryName == "GetInjuries":
        return supabase.table("Injury").select(
            "InjuryStartDate, InjuryEndDate, Player(PlayerName), OSIICS(OSIICS_Diagnosis)"
            ).execute().data
    
    if QueryName == "GetPlayers":
        return supabase.table("Player").select("*").execute().data
    
    if QueryName == "GetOSIICS":
        return supabase.table("OSIICS").select("*").execute().data