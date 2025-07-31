# streamlit_app.py
import streamlit as st
from utils.database import init_connection

st.session_state.supabase = init_connection()


st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

st.write("# Welcome to the Physio App! 👋")

st.markdown(
    """
    This web application has been designed for the workflow of sports physio's.
    Select a web page from the left for your desired workflow.
"""
)
