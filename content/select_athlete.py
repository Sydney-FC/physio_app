import pandas as pd
import streamlit as st


def select_athlete(athlete_df: pd.DataFrame):

    if "athlete_name" in athlete_df.columns:
        athletes = athlete_df["athlete_name"].tolist()
    else:
        # If column name is different, show available columns for debugging
        st.error(
            f"Column 'athlete_name' not found. Available columns: {list(athlete_df.columns)}"
        )
        athletes = []

    selected_athlete = st.selectbox("Select a athlete", athletes, index=None)

    if selected_athlete is not None:
        athlete_id = athlete_df.loc[
            athlete_df["athlete_name"] == selected_athlete, "athlete_id"
        ].values[0]
        st.write(f"Placeholder performance data for {selected_athlete}")
        
        return athlete_id
