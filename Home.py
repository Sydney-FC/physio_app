import streamlit as st
from streamlit.dataframe_util import Data
from streamlit.runtime.state import session_state
from utils.database import *

from content.select_athlete import select_athlete
from content.injuries import display_injuries, render_add_injury_form, render_update_injury_form

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
    # Store consistently under 'athlete_data'
    st.session_state.athlete_data = athlete_df

st.title("Players")

athlete_id = select_athlete(athlete_df)

if athlete_id:
    
    if "adding_injury" not in st.session_state:
        st.session_state.adding_injury = False

    # Add Injury control at the top
    if st.button("Add Injury"):
        st.session_state.adding_injury = not st.session_state.adding_injury

    if st.session_state.adding_injury:
        render_add_injury_form(
            athlete_id,
            get_moi(supabase),
            get_moo(supabase),
            get_osiics(supabase)
        )

    injuries_df = st.session_state.get("injuries")

    if injuries_df is None:
        injuries_df = pd.DataFrame(get_injuries(supabase, athlete_id))
        st.session_state.injuries = injuries_df

    display_injuries(injuries_df)
