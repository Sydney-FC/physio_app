import streamlit as st
import pandas as pd


def display_injuries(injuries_df: pd.DataFrame):
    st.dataframe(injuries_df)


def render_injury_insertion():
    st.write("Insert Injury")


def render_add_injury_form(moi_options: dict, moo_options: dict):
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Starting Date")
        rpt = st.date_input("Return To Partial Training", value=None)
        rpg = st.date_input("Return To Partial Games", value=None)
        ftfg = st.date_input("Return To Full Training, Full Games", value=None)

    with col2:
        st.write("Osiics Select here")

        selected_moi = st.selectbox(
            "Mechanism of Injury", options=moi_options.keys(), index=None
        )

        moi_id = moi_options.get(selected_moi)

        selected_moo = st.selectbox(
            "Method of Onset", options=moo_options.keys(), index=None
        )

        moo_id = moo_options.get(selected_moo)


def render_update_injury_form():

    pass
