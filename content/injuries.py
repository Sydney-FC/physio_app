from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import date
from utils.database import (
    get_injuries,
    insert_injury,
    insert_injury_note,
    update_injury,
)


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


def render_update_injury_form(
    athlete_id: str,
    injuries_df: pd.DataFrame,
    moi_options: dict,
    moo_options: dict,
    osiics_options: dict,
):
    if injuries_df is None or injuries_df.empty:
        st.info("No injuries available to update.")
        return

    # Ensure we have a simple dataframe copy to avoid pandas SettingWithCopy warnings
    injuries_df = injuries_df.copy()

    injury_rows = injuries_df.to_dict("records")
    injury_map: dict[str, str] = {}

    for row in injury_rows:
        injury_id = row.get("injury_id")
        if not injury_id:
            continue
        start_date = row.get("start_date") or "Unknown start"
        osiics_code = row.get("osiics_code") or "Unknown OSIICS"
        label = f"{start_date} – {osiics_code}"
        injury_map[label] = injury_id

    if not injury_map:
        st.info("No injuries available to update.")
        return

    option_labels = list(injury_map.keys())

    # Restore previous selection if present
    selected_injury_id = st.session_state.get("selected_injury_id")
    default_index = 0
    if selected_injury_id:
        for idx, label in enumerate(option_labels):
            if injury_map[label] == selected_injury_id:
                default_index = idx
                break

    selected_label = st.selectbox(
        "Select injury to update", option_labels, index=default_index
    )
    selected_injury_id = injury_map[selected_label]
    st.session_state.selected_injury_id = selected_injury_id

    # Retrieve the selected injury row
    selected_row = next(
        (row for row in injury_rows if row.get("injury_id") == selected_injury_id), None
    )

    if not selected_row:
        st.error("Unable to load the selected injury.")
        return

    def _parse_date(value) -> date | None:
        if not value:
            return None
        try:
            return pd.to_datetime(value).date()
        except Exception:
            return None

    current_start = _parse_date(selected_row.get("start_date")) or date.today()
    current_rpt = _parse_date(selected_row.get("rpt"))
    current_rpg = _parse_date(selected_row.get("rpg"))
    current_ftdg = _parse_date(selected_row.get("ftdg"))

    def _with_none_option(options_dict: dict[str, str]):
        labels = list(options_dict.keys())
        return ["None"] + labels

    def _default_index(options_dict: dict[str, str], labels: list[str], current_value):
        if current_value is None:
            return 0
        for label, value in options_dict.items():
            if value == current_value and label in labels:
                return labels.index(label)
        return 0

    with st.form("update_injury_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input("Starting Date", value=current_start)
            rpt = st.date_input("Return To Partial Training", value=current_rpt)
            rpg = st.date_input("Return To Partial Games", value=current_rpg)
            ftdg = st.date_input(
                "Return To Full Training, Full Games", value=current_ftdg
            )

        with col2:
            osiics_labels = list(osiics_options.keys())
            if not osiics_labels:
                st.error("No OSIICS options available. Cannot update injury.")
                return

            current_osiics_label = next(
                (label for label, code in osiics_options.items()
                 if code == selected_row.get("osiics_code")),
                None,
            )
            osiics_index = (
                osiics_labels.index(current_osiics_label)
                if current_osiics_label in osiics_labels
                else 0
            )
            selected_osiics_label = st.selectbox(
                "OSIICS Diagnosis",
                options=osiics_labels,
                index=osiics_index,
            )
            osiics_code = osiics_options.get(selected_osiics_label)

            moi_labels = _with_none_option(moi_options)
            moi_index = _default_index(
                moi_options, moi_labels, selected_row.get("moi_id")
            )
            selected_moi_label = st.selectbox(
                "Mechanism of Injury", options=moi_labels, index=moi_index
            )
            moi_id = (
                None
                if selected_moi_label == "None"
                else moi_options.get(selected_moi_label)
            )

            moo_labels = _with_none_option(moo_options)
            moo_index = _default_index(
                moo_options, moo_labels, selected_row.get("moo_id")
            )
            selected_moo_label = st.selectbox(
                "Mode of Onset", options=moo_labels, index=moo_index
            )
            moo_id = (
                None
                if selected_moo_label == "None"
                else moo_options.get(selected_moo_label)
            )

        notes = st.text_area(
            "Add note (optional)",
            placeholder="Add details/context about this update...",
        )

        submit_col, cancel_col = st.columns([1, 1])
        submit = submit_col.form_submit_button("Save Changes", use_container_width=True)
        cancel = cancel_col.form_submit_button("Cancel", use_container_width=True)

    if cancel:
        st.session_state.updating_injury = False
        st.session_state.selected_injury_id = None
        return

    if submit:
        errors: list[str] = []
        if not athlete_id:
            errors.append("No athlete selected.")
        if not start_date:
            errors.append("Starting Date is required.")
        if not osiics_code:
            errors.append("OSIICS diagnosis is required.")

        if errors:
            for error in errors:
                st.error(error)
            return

        supabase = st.session_state.get("supabase")
        if not supabase:
            st.error("Database connection not available.")
            return

        def _serialize(d: date | None) -> str | None:
            return d.isoformat() if d else None

        payload = {
            "athlete_id": athlete_id,
            "start_date": _serialize(start_date),
            "rpt": _serialize(rpt),
            "rpg": _serialize(rpg),
            "ftdg": _serialize(ftdg),
            "osiics_code": osiics_code,
            "moi_id": moi_id,
            "moo_id": moo_id,
        }

        updated_row = update_injury(supabase, selected_injury_id, payload)
        if updated_row:
            if notes:
                try:
                    insert_injury_note(supabase, selected_injury_id, notes)
                except Exception:
                    st.warning("Injury updated, but failed to save note.")

            try:
                df = pd.DataFrame(get_injuries(supabase, athlete_id))
                st.session_state.injuries = df
            except Exception:
                pass

            st.success("Injury updated.")
            st.session_state.updating_injury = False
            st.session_state.selected_injury_id = None
        else:
            st.error("Failed to update injury. Please try again.")
