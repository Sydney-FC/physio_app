import re
import plotly.express as px
from supabase import create_client, Client
import streamlit as st
import pandas as pd

def get_ID(selected):
    selected = re.findall(r'\d+', selected)
    return int(selected[0])

def get_Notes_ID(selected):
    date = re.search(r'\d{4}-\d{2}-\d{2}', selected)
    date_str = date.group()

    IDs = re.search(r'\((\d+)/(\d+)\)', selected)
    PlayerID = IDs.group(1)
    OSIICS_ID = IDs.group(2)
    return PlayerID, OSIICS_ID, date_str

def create_edit_injury_options(dataframe):
    row_labels = []

    for index, row in dataframe.iterrows():
        InjuryStartDate = row["InjuryStartDate"]
        PlayerName = row["Player"]
        OSIICS_Disagnosis = row["OSIICS_Diagnosis"]

        row_labels.append(f"{InjuryStartDate} / {PlayerName} / {OSIICS_Disagnosis}")
    
    return row_labels

def notes_options(injury_dataframe):
    options = []
    for index, row in injury_dataframe.iterrows():
        PlayerID = row["PlayerID"]
        PlayerName = row["PlayerName"]
        OSIICS_ID = row["OSIICS_ID"]
        OSIICS_Diagnosis = row["OSIICS_Diagnosis"]
        InjuryStartDate = row["InjuryStartDate"]
        options.append(f"{PlayerName}, {OSIICS_Diagnosis}, {InjuryStartDate}. IDs ({PlayerID}/{OSIICS_ID}).")

    return options

def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def run_query(QueryName: str):

    if QueryName == "GetNotes":

        data = supabase.table("InjuryNote").select(
            "InjuryNoteDate, InjuryNoteMessage, InjuryStartDate, Injury(OSIICS(OSIICS_Diagnosis), Player(PlayerName))"
        ).execute().data

        flattened = []
        for row in data:
            flattened.append({
                "PlayerName": row["Injury"]["Player"]["PlayerName"],
                "OSIICS_Diagnosis": row["Injury"]["OSIICS"]["OSIICS_Diagnosis"],
                "InjuryStartDate": row["InjuryStartDate"],
                "InjuryNoteDate": row["InjuryNoteDate"],
                "InjuryNoteMessage": row["InjuryNoteMessage"]
            })

        return flattened

    if QueryName == "GetInjuries":
        
        data = supabase.table("Injury").select(
            "InjuryStartDate, InjuryEndDate, Player(PlayerID, PlayerName), OSIICS(*)"
            ).execute().data
        
        flattened = []
        for r in data:
            flattened.append({
                "InjuryStartDate": r["InjuryStartDate"],
                "InjuryEndDate": r["InjuryEndDate"],
                "PlayerID": r["Player"]["PlayerID"],
                "PlayerName": r["Player"]["PlayerName"],
                "OSIICS_ID": r["OSIICS"]["OSIICS_ID"],
                "OSIICS_Diagnosis": r["OSIICS"]["OSIICS_Diagnosis"],
                "OSIICS_BodyPart": r["OSIICS"]["OSIICS_BodyPart"],
                "OSIICS_TissueType": r["OSIICS"]["OSIICS_TissueType"],
                "OSIICS_PathologyType": r["OSIICS"]["OSIICS_PathologyType"]
            })
        
        return flattened
    
    if QueryName == "GetPlayers":
        return supabase.table("Player").select("*").execute().data
    
    if QueryName == "GetOSIICS":
        return supabase.table("OSIICS").select("*").execute().data
    
def osiics_summary(df_injury_data, column):
    summary = df_injury_data[column].value_counts().reset_index()
    summary.columns = [column, "count"]
    summary["proportion"] = summary["count"] / summary["count"].sum()
    return summary

def osiics_charts(df_summary, column):
    fig_bar = px.bar(df_summary, x = column, y = "count", title = f"Injury Counts by {column}", text = "count")
    fig_pie = px.pie(df_summary, names = column, values = "proportion", title = f"Injury Proportion by {column}")
    return fig_bar, fig_pie
