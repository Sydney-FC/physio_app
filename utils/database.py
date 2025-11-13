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
    # Debug: Check what columns actually exist in the injury table
    try:
        test_resp = supabase.table("injury").select("*").limit(1).execute()
        if test_resp.data and test_resp.data[0]:
            available_columns = list(test_resp.data[0].keys())
            print(f"DEBUG: Available columns in injury table: {available_columns}")
        else:
            print("DEBUG: injury table exists but has no data to check columns")
    except Exception as e:
        print(f"DEBUG: Error checking injury table schema: {e}")

    # Try to handle potential column name variations
    original_payload = payload.copy()

    # If payload has ossics_code but table might expect osiics_code (or vice versa)
    if "ossics_code" in payload:
        # First try with the original payload
        try:
            resp = supabase.table("injury").insert(payload).execute()
            data = getattr(resp, "data", None)
            return data[0] if data and isinstance(data, list) and data else None
        except Exception as e:
            if "ossics_code" in str(e) and "Could not find" in str(e):
                print(
                    f"DEBUG: Original ossics_code failed, trying osiics_code variant: {e}"
                )
                # Try with osiics_code instead
                modified_payload = payload.copy()
                modified_payload["osiics_code"] = modified_payload.pop("ossics_code")
                try:
                    resp = supabase.table("injury").insert(modified_payload).execute()
                    data = getattr(resp, "data", None)
                    return data[0] if data and isinstance(data, list) and data else None
                except Exception as e2:
                    print(f"DEBUG: osiics_code variant also failed: {e2}")
                    raise e  # Re-raise the original error
            else:
                raise e
    else:
        # Standard insert if no ossics_code in payload
        resp = supabase.table("injury").insert(payload).execute()
        data = getattr(resp, "data", None)
        return data[0] if data and isinstance(data, list) and data else None


def update_injury(supabase: Client, injury_id: str, payload: dict) -> dict | None:
    """Update an injury row by injury_id. Returns the updated row or None on failure."""

    if not injury_id:
        return None

    resp = supabase.table("injury").update(payload).eq("injury_id", injury_id).execute()
    data = getattr(resp, "data", None)
    return data[0] if data and isinstance(data, list) and data else None


def insert_injury_note(
    supabase: Client, injury_id: str, note_content: str
) -> dict | None:
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
