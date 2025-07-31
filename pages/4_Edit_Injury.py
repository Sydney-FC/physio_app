import streamlit as st
import re
from supabase import create_client, Client

from utils.database import run_query
from utils.func import get_ID, create_edit_injury_options
from utils.options import create_options

### Database

supabase = st.session_state.get("supabase")

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

row_labels = create_edit_injury_options(injury_data)

### Streamlit Page

st.header("Edit an Existing Injury")

st.data_editor(row_labels)

selected_label = st.selectbox("Select Injury Entry", row_labels)

with st.form("edit_injury"):
    player = st.selectbox(label = "Player Name", options = player_options)
    osiics = st.selectbox(label = "OSIICS Diagnosis", options = OSIICS_options)
    injury_start_date = st.date_input(label = "Injury Start Date")
    injury_end_date = st.date_input(label = "Injury End Date")
    submitted = st.form_submit_button("Update")

    if submitted:
        player_id = get_ID(player)
        osiics_id = get_ID(osiics)

        update_response = supabase.table("Injury").update({
            "PlayerID": player_id,
            "InjuryStartDate": str(injury_start_date),
            "OSIICS_ID": osiics_id,
            "InjuryEndDate": str(injury_end_date)
        }).match({
            "PlayerID": player_id,
            "InjuryStartDate": str(injury_start_date),
            "OSIICS_ID": osiics_id,
        }).execute()

        st.success(f"Injury '{osiics}' to '{player}' on '{injury_start_date}' edited successfully!") 
