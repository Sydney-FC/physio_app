import streamlit as st
import pandas as pd


def display_injuries(injuries_df: pd.DataFrame):
    st.dataframe(injuries_df)
    
def render_injury_insertion():
    st.write("Insert Injury")
