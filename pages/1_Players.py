import streamlit as st
from utils.database import run_query, init_connection
from fuzzywuzzy.process import extract
from pandas import DataFrame as df


# Initialise connection.
supabase = st.session_state.get("supabase")

if not supabase:
    supabase = init_connection()
    st.session_state.supabase = supabase


player_data = df(run_query("GetPlayers"))


st.title("Players")

# Create two columns for the buttons
col1, col2 = st.columns(2)

with col1:
    show_all_players = st.button("View All Players", use_container_width=True)

with col2:
    show_add_player = st.button("Add New Player", use_container_width=True)

# Initialize session states for button toggles
if 'show_players' not in st.session_state:
    st.session_state.show_players = False
if 'show_add_form' not in st.session_state:
    st.session_state.show_add_form = False
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None

# Handle button clicks
if show_all_players:
    st.session_state.show_players = not st.session_state.show_players
    st.session_state.show_add_form = False  # Hide the other section
    st.session_state.selected_player = None  # Clear selected player

if show_add_player:
    st.session_state.show_add_form = not st.session_state.show_add_form
    st.session_state.show_players = False  # Hide the other section
    st.session_state.selected_player = None  # Clear selected player

# Show All Players section
if st.session_state.show_players:
    st.header("All Players in Database")
    
    st.dataframe(player_data, use_container_width=True)
    st.info(f"Total players: {len(player_data)}")

# Show Add Player section
if st.session_state.show_add_form:
    st.header("Add a New Player")

    with st.form("add_player_form"):
        PlayerName = st.text_input("Player Name")
        PlayerYOB = st.text_input("Year of Birth")
        PlayerPosition = st.text_input("Player Position")
        submitted = st.form_submit_button("Add Player")

        if submitted:
            if not PlayerName:
                st.warning("Player name is required.")
            else:
                # Insert into Supabase
                response = supabase.table("Player").insert({
                    "PlayerName": PlayerName,
                    "PlayerYOB": str(PlayerYOB),  # Convert date to string
                    "PlayerPosition": PlayerPosition
                }).execute()

                st.success(f"Player '{PlayerName}' added successfully!")
                # Optionally refresh the page or clear the form

if st.session_state.selected_player is None:
    query = st.text_input("Search Players", key="search_query")
else:
    query = ""

if query != "" and st.session_state.selected_player is None:
    top_n = extract(query, player_data['PlayerName'].to_list(), limit=10)
    
    # Create horizontal layout for player buttons
    buttons_per_row = 4
    for i in range(0, len(top_n), buttons_per_row):
        cols = st.columns(buttons_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(top_n):
                player, ratio = top_n[i + j]
                with col:
                    if st.button(player, use_container_width=True, key=f"btn_{i}_{j}"):
                        st.session_state.selected_player = player
                        st.rerun()

# Show selected player details
if st.session_state.selected_player:
    selected_player_name = st.session_state.selected_player
    
    # Find player data
    player_info = player_data[player_data['PlayerName'] == selected_player_name]
    
    if not player_info.empty:
        player_row = player_info.iloc[0]
        
        # Back button
        if st.button("← Back to Search"):
            st.session_state.selected_player = None
            st.rerun()
        
        st.header(f"👤 {selected_player_name}")
        
        # Display player info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Player ID", player_row.get('PlayerID', 'N/A'))
        
        with col2:
            birth_year = player_row.get('PlayerYOB', 'N/A')
            if str(birth_year).isdigit():
                age = 2024 - int(birth_year)
                st.metric("Age", f"{age} years")
            else:
                st.metric("Birth Year", birth_year)
        
        with col3:
            st.metric("Position", player_row.get('PlayerPosition', 'N/A'))
        
        # Get player injuries and notes
        player_id = player_row.get('PlayerID')
        
        # Fetch injury data
        all_injuries = run_query("GetInjuries")
        player_injuries = [injury for injury in all_injuries if injury.get('PlayerID') == player_id]
        
        all_notes = run_query("GetNotes")
        player_notes = [note for note in all_notes if note.get('PlayerName') == selected_player_name]
        
        st.markdown("---")
        st.subheader("🏥 Injury History")
        
        # Injury summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Injuries", len(player_injuries))
        with col2:
            active_injuries = len([inj for inj in player_injuries if not inj.get('InjuryEndDate')])
            st.metric("Active Injuries", active_injuries)
        with col3:
            resolved_injuries = len([inj for inj in player_injuries if inj.get('InjuryEndDate')])
            st.metric("Resolved Injuries", resolved_injuries)
        
        # Display injuries if any exist
        if player_injuries:
            st.subheader("📋 Injury Records")
            injuries_df = df(player_injuries)
            
            # Select relevant columns for display
            display_columns = ['InjuryStartDate', 'InjuryEndDate', 'OSIICS_Diagnosis', 'OSIICS_BodyPart', 'OSIICS_TissueType']
            available_columns = [col for col in display_columns if col in injuries_df.columns]
            
            if available_columns:
                display_df = injuries_df[available_columns].copy()
                # Replace None/empty end dates with "Active"
                if 'InjuryEndDate' in display_df.columns:
                    display_df['InjuryEndDate'] = display_df['InjuryEndDate'].fillna('Active')
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Display injury notes if any exist
        if player_notes:
            st.subheader("📝 Injury Notes")
            notes_df = df(player_notes)
            
            display_columns = ['InjuryNoteDate', 'OSIICS_Diagnosis', 'InjuryNoteMessage']
            available_columns = [col for col in display_columns if col in notes_df.columns]
            
            if available_columns:
                display_df = notes_df[available_columns]
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Show message if no injury data
        if not player_injuries and not player_notes:
            st.info("No injury records found for this player.")