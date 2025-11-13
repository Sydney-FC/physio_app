import pandas as pd
import streamlit as st


def select_athlete(athlete_df: pd.DataFrame):
    """Render athlete selector, persist selection, and clear dependent state when it changes.

    - Stores selected athlete name/id in st.session_state
    - Clears cached data (e.g., injuries) when selection changes so downstream reloads
    - Returns selected athlete_id or None
    """

    required = {"athlete_name", "athlete_id"}
    if not required.issubset(set(athlete_df.columns)):
        st.error(
            f"Missing required columns: {required - set(athlete_df.columns)}. "
            f"Available: {list(athlete_df.columns)}"
        )
        return None

    athlete_names = athlete_df["athlete_name"].tolist()

    # Previous selection (if any)
    prev_id = st.session_state.get("selected_athlete_id")
    prev_name = st.session_state.get("selected_athlete_name")

    # Compute default index if we have a previous selection
    default_index = None
    if prev_name in athlete_names:
        try:
            default_index = athlete_names.index(prev_name)
        except ValueError:
            default_index = None

    # on_change callback to persist selection, clear dependent state, and rerun immediately
    def _on_select_change():
        name = st.session_state.get("athlete_select")
        if not name:
            return
        # Resolve new athlete_id
        new_id = (
            athlete_df.loc[athlete_df["athlete_name"] == name, "athlete_id"].iloc[0]
        )
        old_id = st.session_state.get("selected_athlete_id")
        # If changed, clear downstream cached data and UI toggles
        if old_id != new_id:
            for key in ["injuries"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state["adding_injury"] = False
        # Persist selection
        st.session_state["selected_athlete_name"] = name
        st.session_state["selected_athlete_id"] = new_id
        # Force immediate rerun so the page reflects the new athlete in one interaction
        st.rerun()

    selected_name = st.selectbox(
        "Select an athlete",
        athlete_names,
        index=default_index,
        key="athlete_select",
        placeholder="Choose a player",
        on_change=_on_select_change,
    )

    if not selected_name:
        return None

    # Lookup id from selected name
    athlete_id = (
        athlete_df.loc[athlete_df["athlete_name"] == selected_name, "athlete_id"]
        .iloc[0]
    )

    # Persist current selection if not already persisted by the on_change path
    # (e.g., first render where user hasn't interacted yet)
    if st.session_state.get("selected_athlete_id") != athlete_id:
        st.session_state["selected_athlete_name"] = selected_name
        st.session_state["selected_athlete_id"] = athlete_id

    return athlete_id
