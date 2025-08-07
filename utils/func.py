import re
import plotly.express as px
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

def create_edit_injury_options(dataframe: pd.DataFrame):
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


    
def osiics_summary(df_injury_data, column):
    summary = df_injury_data[column].value_counts().reset_index()
    summary.columns = [column, "count"]
    summary["proportion"] = summary["count"] / summary["count"].sum()
    return summary

def osiics_charts(df_summary, column):
    fig_bar = px.bar(df_summary, x = column, y = "count", title = f"Injury Counts by {column}", text = "count")
    fig_pie = px.pie(df_summary, names = column, values = "proportion", title = f"Injury Proportion by {column}")
    return fig_bar, fig_pie
