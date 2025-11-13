import streamlit as st
from supabase import create_client, Client


def init_connection() -> Client:
    """Initialize a connection to the Supabase database using credentials from Streamlit secrets."""

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def get_injuries(supabase: Client, athlete_id: str) -> list[dict]:
    """Fetch injuries with related player and OSIICS information."""

    return (
        supabase.table("injury").select("*").eq("athlete_id", athlete_id).execute().data
    )


def get_moi(supabase: Client) -> dict:
    result = supabase.table("mechanism_of_injury").select("*").execute().data
    return {
        f"{item['injury']} ({item['type_of_contact']}) - {item['description']}": item[
            "moi_id"
        ]
        for item in result
    }


def get_moo(supabase: Client) -> dict:
    result = supabase.table("mode_of_onset").select("*").execute().data

    return {
        f"{item['mechanism']} - {item['presentaion']}": item["moo_id"]
        for item in result
    }


def get_athletes(supabase: Client) -> list[dict]:
    """Fetch all athletes from the database."""

    return supabase.table("athlete").select("*").execute().data


def insert_injury(supabase: Client, payload: dict) -> dict | None:
    """Insert a new injury row. Returns inserted row (incl. injury_id) or None on failure.

    Required keys per schema: athlete_id, ossics_code, start_date
    Optional keys: moo_id, moi_id, rpt, rpg, ftdg
    Notes are stored in injury_notes table separately.
    """
    resp = supabase.table("injury").insert(payload).select("*").execute()
    data = getattr(resp, "data", None)
    return (data[0] if data and isinstance(data, list) and data else None)


def update_injury(supabase: Client, injury_id: str, payload: dict) -> dict | None:
    """Update an existing injury record and return the updated row, or None on failure."""

    resp = (
        supabase.table("injury")
        .update(payload)
        .eq("injury_id", injury_id)
        .select("*")
        .execute()
    )
    data = getattr(resp, "data", None)
    return (data[0] if data and isinstance(data, list) and data else None)

def insert_injury_note(supabase: Client, injury_id: str, note_content: str) -> dict | None:
    """Insert a note for an injury into injury_notes. Returns inserted row or None."""
    resp = (
        supabase.table("injury_notes")
        .insert({"injury_id": injury_id, "note_content": note_content})
        .execute()
    )
    data = getattr(resp, "data", None)
    return data[0] if data and isinstance(data, list) and data else None


def get_osiics(supabase: Client) -> dict[str, str]:
    """Return OSIICS options as {label: osiics_code}, matching get_moi/get_moo style.

    Label format: "Diagnosis (Bodypart, Tissue, Pathology)" where optional fields are omitted if null.
    """

    options: dict[str, str] = {}
    page_size = 1000
    start = 0

    while True:
        # Order by primary key to keep paging stable; table name is lowercase in Postgres
        response = (
            supabase.table("osiics")
            .select("*")
            .order("osiics_code", desc=False)
            .range(start, start + page_size - 1)
            .execute()
        )

        rows = response.data or []
        if not rows:
            break

        for item in rows:
            diagnosis = item.get("diagnosis") or ""
            # Build detail parts, omit missing/empty
            parts = [
                p
                for p in [
                    item.get("bodypart"),
                    item.get("tissue_type"),
                    item.get("pathology_type"),
                ]
                if p
            ]
            label = diagnosis if not parts else f"{diagnosis} ({', '.join(parts)})"
            code = item.get("osiics_code")
            if code:
                options[label] = code

        if len(rows) < page_size:
            # Last page
            break

        start += page_size

    return options
