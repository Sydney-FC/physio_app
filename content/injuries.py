import streamlit as st
import pandas as pd
from utils.database import (
    insert_injury,
    update_injury,
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
    updating_id = st.session_state.get("updating_injury_id")

    for idx, row in enumerate(records):
        injury_key = row.get("injury_id", idx)
        # DB column is 'ossics_code' (FK to osiics.osiics_code)
        diagnosis_label = osiics_by_code.get(row.get("osiics_code"))
        start_label = _fmt_date(row.get("start_date"))

        with st.container():
            if updating_id and row.get("injury_id") == updating_id:
                st.markdown(
                    f"### Update Injury{f': {diagnosis_label}' if diagnosis_label else ''}"
                )
                st.caption(f"Start Date: {start_label}")
                render_update_injury_form()
                st.divider()
                continue

            header_cols = st.columns([0.75, 0.25])
            with header_cols[0]:
                st.markdown(f"### {diagnosis_label}")
                st.caption(f"Start Date: {start_label}")
            with header_cols[1]:
                if st.button(
                    "Update",
                    key=f"update_injury_{injury_key}",
                    use_container_width=True,
                    disabled=not row.get("injury_id"),
                ):
                    st.session_state.updating_injury_id = row.get("injury_id")
                    st.session_state.updating_injury_data = dict(row)
                    st.session_state.adding_injury = False

            info_cols = st.columns(2)
            with info_cols[0]:
                st.markdown(
                    f"**Mechanism of Injury**: {moi_by_id.get(row.get('moi_id')) or '—'}"
                )
                st.markdown(
                    f"**Mode of Onset**: {moo_by_id.get(row.get('moo_id')) or '—'}"
                )
            with info_cols[1]:
                st.markdown(
                    f"**Return to Partial Training**: {_fmt_date(row.get('rpt'))}"
                )
                st.markdown(
                    f"**Return to Partial Games**: {_fmt_date(row.get('rpg'))}"
                )
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
    injury_id = st.session_state.get("updating_injury_id")
    injury_data = st.session_state.get("updating_injury_data") or {}

    if not injury_id:
        st.warning("No injury selected for update.")
        return

    supabase = st.session_state.get("supabase")
    if not supabase:
        st.error("Database connection not available.")
        return

    athlete_id = injury_data.get("athlete_id") or st.session_state.get(
        "selected_athlete_id"
    )

    moi_options = get_moi(supabase)
    moo_options = get_moo(supabase)
    osiics_options = get_osiics(supabase)

    def _to_date(value):
        if not value:
            return None
        try:
            return pd.to_datetime(value).date()
        except Exception:
            return None

    def _label_for_id(options: dict, identifier):
        for label, option_id in options.items():
            if option_id == identifier:
                return label
        return None

    with st.form("update_injury_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Starting Date", value=_to_date(injury_data.get("start_date"))
            )
            rpt = st.date_input(
                "Return To Partial Training",
                value=_to_date(injury_data.get("rpt")),
            )
            rpg = st.date_input(
                "Return To Partial Games",
                value=_to_date(injury_data.get("rpg")),
            )
            ftdg = st.date_input(
                "Return To Full Training, Full Games",
                value=_to_date(injury_data.get("ftdg")),
            )

        with col2:
            osiics_labels = list(osiics_options.keys())
            current_osiics_label = _label_for_id(
                osiics_options, injury_data.get("osiics_code")
            )
            osiics_index = (
                osiics_labels.index(current_osiics_label)
                if current_osiics_label in osiics_labels
                else None
            )
            selected_osiics = st.selectbox(
                "OSIICS Diagnosis",
                options=osiics_labels,
                index=osiics_index,
                placeholder="Select diagnosis",
            )
            osiics_code = osiics_options.get(selected_osiics)

            moi_labels = list(moi_options.keys())
            current_moi_label = _label_for_id(moi_options, injury_data.get("moi_id"))
            moi_index = (
                moi_labels.index(current_moi_label)
                if current_moi_label in moi_labels
                else None
            )
            selected_moi = st.selectbox(
                "Mechanism of Injury",
                options=moi_labels,
                index=moi_index,
                placeholder="Select MOI",
            )
            moi_id = moi_options.get(selected_moi)

            moo_labels = list(moo_options.keys())
            current_moo_label = _label_for_id(moo_options, injury_data.get("moo_id"))
            moo_index = (
                moo_labels.index(current_moo_label)
                if current_moo_label in moo_labels
                else None
            )
            selected_moo = st.selectbox(
                "Mode of Onset",
                options=moo_labels,
                index=moo_index,
                placeholder="Select MOO",
            )
            moo_id = moo_options.get(selected_moo)

        submit_col, cancel_col = st.columns([1, 1])
        submit = submit_col.form_submit_button("Update Injury", use_container_width=True)
        cancel = cancel_col.form_submit_button("Cancel", use_container_width=True)

    if cancel:
        st.session_state.updating_injury_id = None
        st.session_state.updating_injury_data = None
        return

    if submit:
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

        def _d(d):
            return d.isoformat() if d else None

        payload = {
            "athlete_id": athlete_id,
            "start_date": _d(start_date),
            "rpt": _d(rpt),
            "rpg": _d(rpg),
            "ftdg": _d(ftdg),
            "osiics_code": osiics_code,
            "moi_id": moi_id,
            "moo_id": moo_id,
        }

        updated = update_injury(supabase, injury_id, payload)

        if updated:
            st.success("Injury updated.")
            try:
                df = pd.DataFrame(get_injuries(supabase, athlete_id))
                st.session_state.injuries = df
            except Exception:
                pass
            st.session_state.updating_injury_id = None
            st.session_state.updating_injury_data = None
        else:
            st.error("Failed to update injury. Please try again.")
