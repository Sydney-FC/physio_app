import streamlit as st
from supabase import create_client, Client

# Initialise connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Perform query.
@st.cache_data()
def run_query():
    return supabase.table("Player").select("*").execute().data

rows = run_query()

st.header("All Players in Database")
st.dataframe(rows)

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