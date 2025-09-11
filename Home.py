import streamlit as st
from streamlit.dataframe_util import Data
from utils.database import *

from content.select_athlete import select_athlete
from content.injuries import display_injuries

import pandas as pd


st.set_page_config(
    page_title="Physio App",
)

supabase = st.session_state.get("supabase")

if not supabase:
    supabase = init_connection()
    st.session_state.supabase = supabase

athlete_df = st.session_state.get("athlete_data")

if athlete_df is None:
    athlete_df = pd.DataFrame(get_athletes(supabase))
    st.session_state.player_data = athlete_df

st.title("Players")

athlete_id = select_athlete(athlete_df)

if athlete_id:
    
    
    injuries_df = st.session_state.get("injuries")
    
    if injuries_df is None:
        injuries_df = pd.DataFrame(get_injuries(supabase, athlete_id))
        st.session_state.injuries = injuries_df
    
    display_injuries(injuries_df)
    