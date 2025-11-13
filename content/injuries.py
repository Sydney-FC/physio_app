import streamlit as st
import pandas as pd
from utils.database import (
    insert_injury,
    get_injuries,
    insert_injury_note,
    get_moi,
    get_moo,
    get_osiics,
)


def _build_lookup_maps():
    supabase = st.session_state.get("supabase")
    if not supabase:
        return {}, {}, {}
    try:
        moi = get_moi(supabase)
        moo = get_moo(supabase)
        osiics = get_osiics(supabase)
    except Exception:
        return {}, {}, {}
    moi_by_id = {v: k for k, v in moi.items() if v is not None}
    moo_by_id = {v: k for k, v in moo.items() if v is not None}
    osiics_by_code = {v: k for k, v in osiics.items() if v is not None}
    return moi_by_id, moo_by_id, osiics_by_code


def _fmt_date(d):
    if not d:
        return "—"
    try:
        if hasattr(d, "strftime"):
            return d.strftime("%Y-%m-%d")
        s = str(d)
        return s[:10]
    except Exception:
        return str(d)


def display_injuries(injuries_df: pd.DataFrame):
    """Render past injuries as readable cards with an Update button per injury."""
    if injuries_df is None or injuries_df.empty:
        st.info("No past injuries recorded.")
        return

    moi_by_id, moo_by_id, osiics_by_code = _build_lookup_maps()
    records = injuries_df.to_dict(orient="records")

    for idx, row in enumerate(records):
        injury_key = row.get("injury_id", idx)
        # DB column is 'ossics_code' (FK to osiics.osiics_code)
        diagnosis_label = osiics_by_code.get(row.get("osiics_code"))
        start_label = _fmt_date(row.get("start_date"))

        header_cols = st.columns([0.75, 0.25])
        with header_cols[0]:
            st.markdown(f"### {diagnosis_label}")
            st.caption(f"Start Date: {start_label}")
        with header_cols[1]:
            st.button(
                "Update", key=f"update_injury_{injury_key}", use_container_width=True
            )

        info_cols = st.columns(2)
        with info_cols[0]:
            st.markdown(
                f"**Mechanism of Injury**: {moi_by_id.get(row.get('moi_id')) or '—'}"
            )
            st.markdown(f"**Mode of Onset**: {moo_by_id.get(row.get('moo_id')) or '—'}")
        with info_cols[1]:
            st.markdown(f"**Return to Partial Training**: {_fmt_date(row.get('rpt'))}")
            st.markdown(f"**Return to Partial Games**: {_fmt_date(row.get('rpg'))}")
            st.markdown(
                f"**Return to Full Training & Games**: {_fmt_date(row.get('ftdg'))}"
            )

        st.divider()


def render_injury_insertion():
    st.write("Insert Injury")


def render_add_injury_form(
    athlete_id: str, moi_options: dict, moo_options: dict, osiics_options: dict
):
    with st.form("add_injury_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input("Starting Date")
            rpt = st.date_input("Return To Partial Training", value=None)
            rpg = st.date_input("Return To Partial Games", value=None)
            ftdg = st.date_input("Return To Full Training, Full Games", value=None)

        with col2:
            selected_osiics = st.selectbox(
                "OSIICS Diagnosis",
                options=list(osiics_options.keys()),
                index=None,
                placeholder="Select diagnosis",
            )
            osiics_code = osiics_options.get(selected_osiics)

            selected_moi = st.selectbox(
                "Mechanism of Injury",
                options=list(moi_options.keys()),
                index=None,
                placeholder="Select MOI",
            )
            moi_id = moi_options.get(selected_moi)

            selected_moo = st.selectbox(
                "Mode of Onset",
                options=list(moo_options.keys()),
                index=None,
                placeholder="Select MOO",
            )
            moo_id = moo_options.get(selected_moo)

        notes = st.text_area("Notes (optional)", placeholder="Add details/context...")

        submit_col, cancel_col = st.columns([1, 1])
        submit = submit_col.form_submit_button("Save Injury", use_container_width=True)
        cancel = cancel_col.form_submit_button("Cancel", use_container_width=True)

    if cancel:
        st.session_state.adding_injury = False
        return

    if submit:
        # Basic validation
        errors = []
        if not athlete_id:
            errors.append("No athlete selected.")
        if not start_date:
            errors.append("Starting Date is required.")
        if not osiics_code:
            errors.append("OSIICS diagnosis is required.")

        if errors:
            for e in errors:
                st.error(e)
            return

        supabase = st.session_state.get("supabase")
        if not supabase:
            st.error("Database connection not available.")
            return

        def _d(d):
            return d.isoformat() if d else None

        payload = {
            "athlete_id": athlete_id,
            "start_date": _d(start_date),
            "rpt": _d(rpt),
            "rpg": _d(rpg),
            "ftdg": _d(ftdg),
            # Insert into injury.ossics_code per schema (references osiics.osiics_code)
            "osiics_code": osiics_code,
            "moi_id": moi_id,
            "moo_id": moo_id,
        }

        row = insert_injury(supabase, payload)
        if row:
            # Insert note if provided into injury_notes table
            if notes and isinstance(row, dict):
                try:
                    insert_injury_note(supabase, row.get("injury_id"), notes)
                except Exception:
                    st.warning("Injury saved, but failed to save note.")

            st.success("Injury saved.")
            # Refresh injuries list and close form
            try:
                df = pd.DataFrame(get_injuries(supabase, athlete_id))
                st.session_state.injuries = df
            except Exception:
                pass

            st.session_state.adding_injury = False
        else:
            st.error("Failed to save injury. Please try again.")


def render_update_injury_form():

    pass
