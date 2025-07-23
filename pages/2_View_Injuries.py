import streamlit as st
import re
from supabase import create_client, Client

### Database

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

response = supabase.table("Injury").select(
    "InjuryStartDate, InjuryEndDate, Player(PlayerName), OSIICS(OSIICS_Diagnosis)"
).execute()

injury_data = response.data

clean_data = []
for row in injury_data:
    clean_row = {
        "InjuryStartDate": row["InjuryStartDate"],
        "InjuryEndDate": row["InjuryEndDate"],
        "Player": row["Player"]["PlayerName"] if row.get("Player") else None,
        "OSIICS": row["OSIICS"]["OSIICS_Diagnosis"] if row.get("OSIICS") else None,
    }
    clean_data.append(clean_row)

### Streamlit Page

st.header("All Injuries in Database")
st.dataframe(clean_data)
