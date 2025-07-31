import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime
from supabase import Client
from utils.func import get_ID, run_query, init_connection, osiics_summary, osiics_charts, notes_options, get_Notes_ID
from utils.options import create_list_options, create_options

supabase = init_connection()

if 'key' not in st.session_state:
    st.session_state['key'] = 'value'

injury_data = run_query("GetInjuries")
player_data = run_query("GetPlayers")
OSIICS_data = run_query("GetOSIICS")
notes_data = run_query("GetNotes")

df_injury_data = pd.DataFrame(injury_data)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["View Injuries", "Add Injury", "Edit Injury", "View Injury Notes", "Add Injury Note"])

with tab1:
    st.header("")
    with st.spinner("Loading Data..."):
        st.subheader("All Injuries")
        st.dataframe(injury_data)
        
        st.markdown("---")

        # OSIICS Body Part
        st.subheader("Body Part")
        bp_summary = osiics_summary(df_injury_data, "OSIICS_BodyPart")
        st.dataframe(bp_summary)

        fig_bar, fig_pie = osiics_charts(bp_summary, "OSIICS_BodyPart")
        st.plotly_chart(fig_bar)
        st.plotly_chart(fig_pie)

        st.markdown("---")

        # OSIICS Tissue Type
        st.subheader("Tissue Type")
        tt_summary = osiics_summary(df_injury_data, "OSIICS_TissueType")
        st.dataframe(tt_summary)

        fig_bar, fig_pie = osiics_charts(tt_summary, "OSIICS_TissueType")
        st.plotly_chart(fig_bar)
        st.plotly_chart(fig_pie)

        st.markdown("---")

        # OSIICS Pathology Type
        st.subheader("Pathology Type")
        pt_summary = osiics_summary(df_injury_data, "OSIICS_PathologyType")
        st.dataframe(pt_summary)

        fig_bar, fig_pie = osiics_charts(pt_summary, "OSIICS_PathologyType")
        st.plotly_chart(fig_bar)
        st.plotly_chart(fig_pie)

with tab2:
    st.header("Add a New Injury")

    player_options = create_list_options(player_data, "Player")

    OSIICS_options = []
    for row in OSIICS_data:
        insert_values = create_options(row["OSIICS_Diagnosis"], row["OSIICS_ID"])
        OSIICS_options.append(insert_values)

    with st.form("add_injury_form"):
        player = st.selectbox(label = "Player Name", options = player_options)
        osiics = st.selectbox(label = "OSIICS Diagnosis", options = OSIICS_options)
        injury_start_date = st.date_input(label = "Injury Start Date")
        submitted = st.form_submit_button("Add Injury")

        if submitted:
            player_id = get_ID(player)
            osiics_id = get_ID(osiics)

            if not player:
                st.warning("Player name is required.")
            else:
                # Insert into Supabase
                response = supabase.table("Injury").insert({
                    "PlayerID": player_id,
                    "InjuryStartDate": str(injury_start_date),
                    "OSIICS_ID": osiics_id,
                }).execute()

                st.success(f"Injury '{osiics}' to '{player}' on '{injury_start_date}' added successfully!") 

with tab3:
    st.header("Edit an Existing Injury")
    # row_labels = create_edit_injury_options(df_injury_data)
    st.data_editor(df_injury_data)

with tab4:
    st.header("Injury Notes")
    player_options = create_list_options(player_data, "Player")
    # Get unique values for OSIICS

    PlayerName = st.multiselect(label="Filter By Athlete", options = player_options)
    O_diagnosis = None
    O_bodypart = None
    O_tissuetype = None
    O_pathologytype = None
    start_date = None
    end_date = None

    # How do i display injury notes? st.write(notes[InjuryNoteMessage])?

with tab5:
    st.header("Add a Note to an Injury")
    st.dataframe(notes_data)

    options = notes_options(df_injury_data)

    with st.form("add_injury_note_form"):
        injury = st.selectbox(label = "Select Injury", options = options)
        note = st.text_area(label = "Enter Note")
        submitted = st.form_submit_button("Add Injury")

        if submitted:
            PlayerID, OSIICS_ID, InjuryStartDate = get_Notes_ID(injury)            
            InjuryNoteDate = datetime.today().strftime("%Y-%m-%d")
            InjuryNoteMessage = note

            if not note:
                st.warning("A Note is Required.")
            else:
                # Insert into Supabase
                response = supabase.table("InjuryNote").insert({
                    "PlayerID": PlayerID,
                    "OSIICS_ID": OSIICS_ID,
                    "InjuryStartDate": str(InjuryStartDate),
                    "InjuryNoteDate": str(InjuryNoteDate),
                    "InjuryNoteMessage": InjuryNoteMessage
    
                }).execute()

                st.success(f"Injury '' to '' on '' added successfully!")

