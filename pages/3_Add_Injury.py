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

@st.cache_data()
def run_query(QueryName: str):

    if QueryName == "GetInjuries":
        return supabase.table("Injury").select("*").execute().data
    
    if QueryName == "GetPlayers":
        return supabase.table("Player").select("*").execute().data
    
    if QueryName == "GetOSIICS":
        return supabase.table("OSIICS").select("*").execute().data
    
def create_options(Name: str, x_ID: str):
    return Name + " (ID: " + str(x_ID) + ")"

def get_ID(selected):
    selected = re.findall(r'\d+', selected)
    return int(selected[0])

injury_data = run_query("GetInjuries")
player_data = run_query("GetPlayers")
OSIICS_data = run_query("GetOSIICS")

player_options =[]
for player in player_data:
    insert_values = create_options(player["PlayerName"], player["PlayerID"])
    player_options.append(insert_values)

OSIICS_options = []
for row in OSIICS_data:
    insert_values = create_options(row["OSIICS_Diagnosis"], row["OSIICS_ID"])
    OSIICS_options.append(insert_values)

### Streamlit Page

st.header("Add a New Injury")

with st.form("add_injury_form"):
    player = st.selectbox(label = "Player Name", options = player_options)
    osiics = st.selectbox(label = "OSIICS Diagnosis", options = OSIICS_options)
    injury_start_date = st.date_input(label = "Injury Start Date")
    submitted = st.form_submit_button("Add Injury")

    if submitted:
        player_id = get_ID(player)
        osiics_id = get_ID(osiics)

        if not player:
            st.warning("Player name is required.")
        else:
            # Insert into Supabase
            response = supabase.table("Injury").insert({
                "PlayerID": player_id,
                "InjuryStartDate": str(injury_start_date),
                "OSIICS_ID": osiics_id,
            }).execute()

            st.success(f"Injury '{osiics}' to '{player}' on '{injury_start_date}' added successfully!") 