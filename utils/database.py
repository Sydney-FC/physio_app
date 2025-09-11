import streamlit as st
from supabase import create_client, Client

def init_connection() -> Client:
    """Initialize a connection to the Supabase database using credentials from Streamlit secrets."""

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def get_injuries(supabase: Client, athlete_id: str) -> list[dict]:
    """Fetch injuries with related player and OSIICS information."""

    return supabase.table("injury").select("*").eq("athlete_id",athlete_id).execute().data
    
    


def get_athletes(supabase: Client) -> list[dict]:
    """Fetch all athletes from the database."""

    return supabase.table("athlete").select("*").execute().data




def get_osiics(supabase: Client) -> list[dict]:
    """Fetch all OSIICS records from the database."""
    
    # Use .range() to get all records, Supabase default limit might be 1000
    all_data = []
    page_size = 1000
    start = 0
    
    while True:
        response = supabase.table("OSIICS").select("*").range(start, start + page_size - 1).execute()
        data = response.data
        
        if not data:  # No more data
            break
            
        all_data.extend(data)
        
        if len(data) < page_size:  # Last page
            break
            
        start += page_size
    
    return all_data