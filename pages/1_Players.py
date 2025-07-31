import streamlit as st
from utils.database import init_connection, run_query

# Initialise connection.
# Uses st.cache_resource to only run once.
supabase = st.session_state.get("supabase")

player_data = run_query("GetPlayers")

st.header("All Players in Database")
st.dataframe(player_data)

st.header("Add a New Player")

with st.form("add_player_form"):
    PlayerName = st.text_input("Player Name")
    PlayerYOB = st.text_input("Year of Birth")
    PlayerPosition = st.text_input("Player Position")
    submitted = st.form_submit_button("Add Player")

    if submitted:
        if not PlayerName:
            st.warning("Player name is required.")
        else:
            # Insert into Supabase
            response = supabase.table("Player").insert({
                "PlayerName": PlayerName,
                "PlayerYOB": str(PlayerYOB),  # Convert date to string
                "PlayerPosition": PlayerPosition
            }).execute()

            st.success(f"Player '{PlayerName}' added successfully!")