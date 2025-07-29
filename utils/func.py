import re
import plotly.express as px
from supabase import create_client, Client
import streamlit as st

def create_options(Name: str, x_ID: str):
    return Name + " (ID: " + str(x_ID) + ")"

def get_ID(selected):
    selected = re.findall(r'\d+', selected)
    return int(selected[0])

def create_edit_injury_options(data):
    row_labels = []

    for row in data:
        row_labels.append(f"{row['InjuryStartDate']} / {row['Player']['PlayerName']} / {row['OSIICS']['OSIICS_Diagnosis']}")
    
    return row_labels

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def run_query(QueryName: str):

    if QueryName == "GetInjuries":
        
        data = supabase.table("Injury").select(
            "InjuryStartDate, InjuryEndDate, Player(PlayerName), OSIICS(*)"
            ).execute().data
        
        flattened = []
        for r in data:
            flattened.append({
                "InjuryStartDate": r["InjuryStartDate"],
                "InjuryEndDate": r["InjuryEndDate"],
                "Player": r["Player"]["PlayerName"],
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
