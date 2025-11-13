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
    st.session_state.player_data = athlete_df

st.title("Players")

athlete_id = select_athlete(athlete_df)

if athlete_id:
    
    injuries_df = st.session_state.get("injuries")
    
    if injuries_df is None:
        injuries_df = pd.DataFrame(get_injuries(supabase, athlete_id))
        st.session_state.injuries = injuries_df
    
    display_injuries(injuries_df)
    
    
    if "adding_injury" not in st.session_state:
        st.session_state.adding_injury = False
    if "updating_injury" not in st.session_state:
        st.session_state.updating_injury = False
    if "selected_injury_id" not in st.session_state:
        st.session_state.selected_injury_id = None

    add_col, update_col = st.columns(2)
    with add_col:
        if st.button("Add Injury", use_container_width=True):
            st.session_state.adding_injury = not st.session_state.adding_injury
            if st.session_state.adding_injury:
                st.session_state.updating_injury = False
    with update_col:
        if st.button("Update Injury", use_container_width=True):
            st.session_state.updating_injury = not st.session_state.updating_injury
            if st.session_state.updating_injury:
                st.session_state.adding_injury = False

    if st.session_state.adding_injury:
        render_add_injury_form(
            athlete_id,
            get_moi(supabase),
            get_moo(supabase),
            get_osiics(supabase)
        )

    if st.session_state.updating_injury:
        render_update_injury_form(
            athlete_id,
            injuries_df,
            get_moi(supabase),
            get_moo(supabase),
            get_osiics(supabase)
        )
