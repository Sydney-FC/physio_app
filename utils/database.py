import streamlit as st
from supabase import create_client, Client

def init_connection() -> Client:
    """Initialize a connection to the Supabase database using credentials from Streamlit secrets."""

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def get_notes(supabase: Client) -> list[dict]:
    """Fetch injury notes with related player and diagnosis information."""
    data = supabase.table("InjuryNote").select(
        "InjuryNoteDate, InjuryNoteMessage, InjuryStartDate, Injury(OSIICS(OSIICS_Diagnosis), Player(PlayerName))"
    ).execute().data

    
    results = []
    for row in data:
        # Check if all nested relationships exist and are not None
        injury = row.get("Injury")
        if injury and injury.get("Player") and injury.get("OSIICS"):
            # Safe to access nested data
            results.append({
                "PlayerName": injury["Player"]["PlayerName"],
                "OSIICS_Diagnosis": injury["OSIICS"]["OSIICS_Diagnosis"],
                "InjuryStartDate": row.get("InjuryStartDate"),
                "InjuryNoteDate": row.get("InjuryNoteDate"),
                "InjuryNoteMessage": row.get("InjuryNoteMessage")
            })
        else:
            # Handle cases where relationships are missing
            results.append({
                "PlayerName": "Unknown Player",
                "OSIICS_Diagnosis": "Unknown Diagnosis",
                "InjuryStartDate": row.get("InjuryStartDate", "Unknown"),
                "InjuryNoteDate": row.get("InjuryNoteDate", "Unknown"),
                "InjuryNoteMessage": row.get("InjuryNoteMessage", "No message")
            })
    
    return results

def get_injuries(supabase: Client) -> list[dict]:
    """Fetch injuries with related player and OSIICS information."""

    data = supabase.table("Injury").select(
        "InjuryStartDate, InjuryEndDate, Player(PlayerID, PlayerName), OSIICS(*)"
    ).execute().data
    return [
        {
            "InjuryStartDate": r["InjuryStartDate"],
            "InjuryEndDate": r["InjuryEndDate"],
            "PlayerID": r["Player"]["PlayerID"],
            "PlayerName": r["Player"]["PlayerName"],
            "OSIICS_ID": r["OSIICS"]["OSIICS_ID"],
            "OSIICS_Diagnosis": r["OSIICS"]["OSIICS_Diagnosis"],
            "OSIICS_BodyPart": r["OSIICS"]["OSIICS_BodyPart"],
            "OSIICS_TissueType": r["OSIICS"]["OSIICS_TissueType"],
            "OSIICS_PathologyType": r["OSIICS"]["OSIICS_PathologyType"]
        }
        for r in data
    ]

def get_players(_supabase: Client) -> list[dict]:
    """Fetch all players from the database."""

    return _supabase.table("Player").select("*").execute().data


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


QUERY_HANDLER: dict[str, callable] = {
    "GetNotes": get_notes,
    "GetInjuries": get_injuries,
    "GetPlayers": get_players,
    "GetOSIICS": get_osiics,
}


def run_query(QueryName: str) -> list[dict]:
    """Run a query by name using the appropriate handler and return the results."""

    supabase = st.session_state.supabase
    handler = QUERY_HANDLER.get(QueryName)
    if handler:
        return handler(supabase)
    else:
        raise ValueError(f"Unknown query name: {QueryName}")
        return []