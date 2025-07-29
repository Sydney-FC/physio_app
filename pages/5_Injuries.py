import streamlit as st
import plotly.express as px
import pandas as pd
import re
from supabase import create_client, Client
from utils.func import create_options, get_ID, create_edit_injury_options, run_query, init_connection, osiics_summary, osiics_charts

supabase = init_connection()

injury_data = run_query("GetInjuries")
player_data = run_query("GetPlayers")
OSIICS_data = run_query("GetOSIICS")
df_injury_data = pd.DataFrame(injury_data)

tab1, tab2, tab3, tab4 = st.tabs(["View Injuries", "Add Injury", "Edit Injury", "Add Injury Note"])

with tab1:
    st.header("")
    with st.spinner("Loading Data..."):
        st.subheader("All Injuries")
        st.dataframe(injury_data)

        # OSIICS Body Part
        st.subheader("Body Part")
        bp_summary = osiics_summary(df_injury_data, "OSIICS_BodyPart")
        st.dataframe(bp_summary)

        fig_bar, fig_pie = osiics_charts(bp_summary, "OSIICS_BodyPart")
        st.plotly_chart(fig_bar)
        st.plotly_chart(fig_pie)

        # OSIICS Tissue Type
        st.subheader("Tissue Type")
        tt_summary = osiics_summary(df_injury_data, "OSIICS_TissueType")
        st.dataframe(tt_summary)

        fig_bar, fig_pie = osiics_charts(tt_summary, "OSIICS_TissueType")
        st.plotly_chart(fig_bar)
        st.plotly_chart(fig_pie)

        # OSIICS Pathology Type
        st.subheader("Pathology Type")
        pt_summary = osiics_summary(df_injury_data, "OSIICS_PathologyType")
        st.dataframe(pt_summary)

        fig_bar, fig_pie = osiics_charts(pt_summary, "OSIICS_PathologyType")
        st.plotly_chart(fig_bar)
        st.plotly_chart(fig_pie)


with tab2:
    st.header("")

with tab3:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg", width=200)