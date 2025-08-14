import streamlit as st
from utils.database import run_query, init_connection
from fuzzywuzzy import fuzz
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
if 'editing_injury_id' not in st.session_state:
    st.session_state.editing_injury_id = None
if 'adding_injury' not in st.session_state:
    st.session_state.adding_injury = False
if 'injury_confirmation' not in st.session_state:
    st.session_state.injury_confirmation = None
if 'adding_note_to_injury' not in st.session_state:
    st.session_state.adding_note_to_injury = None

# Handle button clicks
if show_all_players:
    st.session_state.show_players = not st.session_state.show_players
    st.session_state.show_add_form = False  # Hide the other section
    st.session_state.selected_player = None  # Clear selected player
    st.session_state.editing_injury_id = None  # Clear editing state
    st.session_state.adding_injury = False  # Clear adding state
    st.session_state.adding_note_to_injury = None  # Clear note adding state
    st.session_state.injury_confirmation = None  # Clear confirmation state

if show_add_player:
    st.session_state.show_add_form = not st.session_state.show_add_form
    st.session_state.show_players = False  # Hide the other section
    st.session_state.selected_player = None  # Clear selected player
    st.session_state.editing_injury_id = None  # Clear editing state
    st.session_state.adding_injury = False  # Clear adding state

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
            st.session_state.editing_injury_id = None  # Clear editing state
            st.session_state.adding_injury = False  # Clear adding state
            st.session_state.injury_confirmation = None  # Clear confirmation state
            st.session_state.adding_note_to_injury = None  # Clear note adding state
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
        
        # Fetch all OSIICS records for fuzzy matching
        all_osiics = run_query("GetOSIICS")
        
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("🏥 Injury History")
        with col2:
            if st.button("➕ Add New Injury", use_container_width=True):
                st.session_state.adding_injury = not st.session_state.adding_injury
                st.session_state.editing_injury_id = None  # Clear editing state
                st.rerun()
        
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
        
        # Show injury confirmation if needed
        if st.session_state.injury_confirmation:
            injury_data = st.session_state.injury_confirmation
            
            st.subheader("🔍 Confirm Injury Details")
            st.info(f"Please confirm the injury details before adding:")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Start Date:** {injury_data['start_date']}")
                st.write(f"**End Date:** {injury_data['end_date'] if injury_data['end_date'] else 'Ongoing'}")
                st.write(f"**Your Diagnosis:** {injury_data['user_diagnosis']}")
            
            with col2:
                if injury_data['matched_osiics']:
                    st.success("**Matched OSIICS Record:**")
                    st.write(f"**Diagnosis:** {injury_data['matched_osiics'].get('OSIICS_Diagnosis')}")
                    st.write(f"**Body Part:** {injury_data['matched_osiics'].get('OSIICS_BodyPart')}")
                    st.write(f"**Tissue Type:** {injury_data['matched_osiics'].get('OSIICS_TissueType')}")
                    st.write(f"**Match Score:** {injury_data['match_score']}%")
                else:
                    st.warning("⚠️ **New Record Will Be Created:**")
                    st.write(f"**Diagnosis:** {injury_data['user_diagnosis']}")
                    st.write("**Body Part:** (To be filled later)")
                    st.write("**Tissue Type:** (To be filled later)")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Confirm & Add Injury", use_container_width=True):
                    # Proceed with adding the injury
                    try:
                        if injury_data['matched_osiics']:
                            osiics_id = injury_data['matched_osiics']['OSIICS_ID']
                        else:
                            # Create new OSIICS record
                            osiics_data = {
                                "OSIICS_Diagnosis": injury_data['user_diagnosis'],
                                "OSIICS_BodyPart": "",
                                "OSIICS_TissueType": "",
                                "OSIICS_PathologyType": ""
                            }
                            osiics_response = supabase.table("OSIICS").insert(osiics_data).execute()
                            if osiics_response.data:
                                osiics_id = osiics_response.data[0]['OSIICS_ID']
                            else:
                                st.error("❌ Failed to create new OSIICS record")
                                osiics_id = None
                        
                        if osiics_id:
                            # Create injury record
                            injury_record = {
                                "PlayerID": int(player_id),
                                "OSIICS_ID": osiics_id,
                                "InjuryStartDate": str(injury_data['start_date']),
                                "InjuryEndDate": str(injury_data['end_date']) if injury_data['end_date'] else None
                            }
                            
                            supabase.table("Injury").insert(injury_record).execute()
                            st.success("✅ Injury added successfully!")
                            st.session_state.injury_confirmation = None
                            st.session_state.adding_injury = False
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error adding injury: {str(e)}")
            
            with col2:
                if st.button("🔄 Modify Details", use_container_width=True):
                    st.session_state.injury_confirmation = None
                    # Keep adding_injury = True to go back to form
                    st.rerun()
            
            with col3:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.injury_confirmation = None
                    st.session_state.adding_injury = False
                    st.rerun()

        # Show add injury form if adding
        elif st.session_state.adding_injury:
            st.subheader("➕ Add New Injury")
            
            with st.form("add_injury_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_start_date = st.date_input("Start Date", key="add_injury_start_date")
                    new_end_date = st.date_input("End Date (leave empty if ongoing)", value=None, key="add_injury_end_date")
                
                with col2:
                    new_diagnosis = st.text_input("Diagnosis", placeholder="e.g., Hamstring strain")
                    
                    # Show fuzzy match suggestions as we type
                    if new_diagnosis:
                        # Custom fuzzy matching function for better results
                        def custom_fuzzy_match(query, options):
                            results = []
                            query_lower = query.lower().strip()
                            
                            for option in options:
                                if not option:
                                    continue
                                option_lower = option.lower().strip()
                                
                                # Exact match gets 100%
                                if query_lower == option_lower:
                                    score = 100
                                # Check if option starts with query (high priority)
                                elif option_lower.startswith(query_lower):
                                    score = 95
                                # Check if any word in option starts with query
                                elif any(word.startswith(query_lower) for word in option_lower.split()):
                                    score = 85
                                # Use ratio-based matching (prioritizes overall similarity)
                                else:
                                    # Use ratio instead of partial_ratio to avoid substring issues
                                    ratio_score = fuzz.ratio(query_lower, option_lower)
                                    token_score = fuzz.token_sort_ratio(query_lower, option_lower)
                                    # Take the higher of the two, but cap at 80 to prioritize prefix matches
                                    score = min(80, max(ratio_score, token_score))
                                
                                results.append((option, score))
                            
                            # Sort by score and return top results
                            results.sort(key=lambda x: x[1], reverse=True)
                            return results[:3]
                        
                        diagnosis_matches = custom_fuzzy_match(new_diagnosis, [osiics.get('OSIICS_Diagnosis', '') for osiics in all_osiics])
                        if diagnosis_matches and diagnosis_matches[0][1] > 70:  # Show if match is >70%
                            st.info(f"💡 Similar diagnosis found: {diagnosis_matches[0][0]} ({int(diagnosis_matches[0][1])}% match)")
                
                col1, col2 = st.columns(2)
                with col1:
                    add_injury_submit = st.form_submit_button("💾 Add Injury", use_container_width=True)
                with col2:
                    cancel_add = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                if add_injury_submit:
                    if new_diagnosis:
                        try:
                            # Find best matching OSIICS record using improved fuzzy matching
                            def custom_fuzzy_match_single(query, options):
                                query_lower = query.lower().strip()
                                best_match = None
                                best_score = 0
                                
                                for option in options:
                                    if not option:
                                        continue
                                    option_lower = option.lower().strip()
                                    
                                    # Exact match gets 100%
                                    if query_lower == option_lower:
                                        score = 100
                                    # Check if option starts with query (high priority)
                                    elif option_lower.startswith(query_lower):
                                        score = 95
                                    # Check if any word in option starts with query
                                    elif any(word.startswith(query_lower) for word in option_lower.split()):
                                        score = 85
                                    # Use ratio-based matching (prioritizes overall similarity)
                                    else:
                                        # Use ratio instead of partial_ratio to avoid substring issues
                                        ratio_score = fuzz.ratio(query_lower, option_lower)
                                        token_score = fuzz.token_sort_ratio(query_lower, option_lower)
                                        # Take the higher of the two, but cap at 80 to prioritize prefix matches
                                        score = min(80, max(ratio_score, token_score))
                                    
                                    if score > best_score:
                                        best_score = score
                                        best_match = option
                                
                                return best_match, best_score
                            
                            matched_diagnosis, match_score = custom_fuzzy_match_single(new_diagnosis, [osiics.get('OSIICS_Diagnosis', '') for osiics in all_osiics])
                            
                            best_match_osiics = None
                            
                            if matched_diagnosis and match_score > 75:  # Increased threshold to 75% for better accuracy
                                # Find the OSIICS record with the matching diagnosis
                                for osiics in all_osiics:
                                    if osiics.get('OSIICS_Diagnosis') == matched_diagnosis:
                                        best_match_osiics = osiics
                                        break
                            
                            # Store injury data for confirmation
                            st.session_state.injury_confirmation = {
                                'start_date': new_start_date,
                                'end_date': new_end_date,
                                'user_diagnosis': new_diagnosis,
                                'matched_osiics': best_match_osiics,
                                'match_score': match_score
                            }
                            st.rerun()
                                
                        except Exception as e:
                            st.error(f"❌ Error processing injury: {str(e)}")
                    else:
                        st.warning("⚠️ Diagnosis is required")
                
                if cancel_add:
                    st.session_state.adding_injury = False
                    st.rerun()

        # Display injuries if any exist  
        if player_injuries and not st.session_state.adding_injury and not st.session_state.editing_injury_id:
            st.subheader("📋 Injury Records")
            
            # Check if we're editing an injury
            if st.session_state.editing_injury_id:
                # Find the injury being edited
                editing_injury = None
                for injury in player_injuries:
                    if injury.get('OSIICS_ID') == st.session_state.editing_injury_id:
                        editing_injury = injury
                        break
                
                if editing_injury:
                    st.info(f"✏️ Editing injury: {editing_injury.get('OSIICS_Diagnosis', 'Unknown')}")
                    
                    # Edit form
                    with st.form("edit_injury_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Convert string dates to date objects for the date_input
                            start_date_str = editing_injury.get('InjuryStartDate')
                            end_date_str = editing_injury.get('InjuryEndDate')
                            
                            start_date = st.date_input("Start Date", 
                                value=start_date_str if start_date_str else None, key="edit_injury_start_date")
                            end_date = st.date_input("End Date", 
                                value=end_date_str if end_date_str else None, key="edit_injury_end_date")
                        
                        with col2:
                            diagnosis = st.text_input("Diagnosis", value=editing_injury.get('OSIICS_Diagnosis', ''))
                            body_part = st.text_input("Body Part", value=editing_injury.get('OSIICS_BodyPart', ''))
                            tissue_type = st.text_input("Tissue Type", value=editing_injury.get('OSIICS_TissueType', ''))
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            save_changes = st.form_submit_button("💾 Save Changes", use_container_width=True)
                        with col2:
                            cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
                        with col3:
                            delete_injury = st.form_submit_button("🗑️ Delete Injury", use_container_width=True, type="secondary")
                        
                        if save_changes:
                            try:
                                # Update the injury in the database
                                injury_update = {
                                    "InjuryStartDate": str(start_date) if start_date else None,
                                    "InjuryEndDate": str(end_date) if end_date else None
                                }
                                
                                # Update OSIICS data
                                osiics_update = {
                                    "OSIICS_Diagnosis": diagnosis,
                                    "OSIICS_BodyPart": body_part,
                                    "OSIICS_TissueType": tissue_type
                                }
                                
                                # Update injury table
                                supabase.table("Injury").update(injury_update).eq("OSIICS_ID", editing_injury.get('OSIICS_ID')).execute()
                                
                                # Update OSIICS table
                                supabase.table("OSIICS").update(osiics_update).eq("OSIICS_ID", editing_injury.get('OSIICS_ID')).execute()
                                
                                st.success("✅ Injury updated successfully!")
                                st.session_state.editing_injury_id = None
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error updating injury: {str(e)}")
                        
                        if cancel_edit:
                            st.session_state.editing_injury_id = None
                            st.rerun()
                        
                        if delete_injury:
                            try:
                                # Delete injury (you might want to add confirmation)
                                supabase.table("Injury").delete().eq("OSIICS_ID", editing_injury.get('OSIICS_ID')).execute()
                                st.success("✅ Injury deleted successfully!")
                                st.session_state.editing_injury_id = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error deleting injury: {str(e)}")
            
            else:
                # Display injuries as clickable cards
                for i, injury in enumerate(player_injuries):
                    injury_id = injury.get('OSIICS_ID')
                    
                    # Create a card-like display for each injury
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 1])
                        
                        with col1:
                            st.write(f"**Start:** {injury.get('InjuryStartDate', 'N/A')}")
                        
                        with col2:
                            end_date = injury.get('InjuryEndDate', 'Active')
                            st.write(f"**End:** {end_date}")
                        
                        with col3:
                            st.write(f"**Diagnosis:** {injury.get('OSIICS_Diagnosis', 'N/A')}")
                        
                        with col4:
                            st.write(f"**Body Part:** {injury.get('OSIICS_BodyPart', 'N/A')}")
                        
                        with col5:
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.button("✏️", key=f"edit_injury_{injury_id}", help="Edit injury"):
                                    st.session_state.editing_injury_id = injury_id
                                    st.session_state.adding_note_to_injury = None
                                    st.rerun()
                            with col_b:
                                if st.button("📝", key=f"note_injury_{injury_id}", help="Add note"):
                                    st.session_state.adding_note_to_injury = injury_id
                                    st.session_state.editing_injury_id = None
                                    st.rerun()
                        
                        st.markdown("---")
        
        # Show add note form if adding note to an injury
        if st.session_state.adding_note_to_injury:
            # Find the injury we're adding a note to
            note_injury = None
            for injury in player_injuries:
                if injury.get('OSIICS_ID') == st.session_state.adding_note_to_injury:
                    note_injury = injury
                    break
            
            if note_injury:
                st.subheader(f"📝 Add Note to: {note_injury.get('OSIICS_Diagnosis', 'Unknown Injury')}")
                
                with st.form("add_note_form"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        note_message = st.text_area("Note Message", placeholder="Enter your injury note here...", height=100)
                    
                    with col2:
                        note_date = st.date_input("Note Date", key="add_note_date")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        add_note_submit = st.form_submit_button("💾 Add Note", use_container_width=True)
                    with col2:
                        cancel_note = st.form_submit_button("❌ Cancel", use_container_width=True)
                    
                    if add_note_submit:
                        if note_message.strip():
                            try:
                                # Find the injury record
                                all_injuries_query = supabase.table("Injury").select("*").execute()
                                
                                injury_record = None
                                for inj in all_injuries_query.data:
                                    if (inj.get('PlayerID') == int(player_id) and 
                                        inj.get('OSIICS_ID') == st.session_state.adding_note_to_injury):
                                        injury_record = inj
                                        break
                                
                                if injury_record:
                                    # First, let's check what columns InjuryNote actually has
                                    try:
                                        # Try to get the schema by selecting all columns from one row
                                        sample_note = supabase.table("InjuryNote").select("*").limit(1).execute()
                                        if sample_note.data:
                                            st.write(f"InjuryNote columns: {list(sample_note.data[0].keys())}")
                                        
                                        # Try different possible foreign key patterns
                                        note_data_attempts = [
                                            {
                                                "Injury": injury_record.get('InjuryID') or injury_record.get('id'),
                                                "InjuryNoteDate": str(note_date),
                                                "InjuryNoteMessage": note_message.strip(),
                                                "InjuryStartDate": note_injury.get('InjuryStartDate')
                                            },
                                            {
                                                "injury_id": injury_record.get('InjuryID') or injury_record.get('id'),
                                                "InjuryNoteDate": str(note_date),
                                                "InjuryNoteMessage": note_message.strip(),
                                                "InjuryStartDate": note_injury.get('InjuryStartDate')
                                            },
                                            {
                                                "InjuryNoteDate": str(note_date),
                                                "InjuryNoteMessage": note_message.strip(),
                                                "InjuryStartDate": note_injury.get('InjuryStartDate')
                                            }
                                        ]
                                        
                                        # Try each data structure
                                        success = False
                                        for i, note_data in enumerate(note_data_attempts):
                                            try:
                                                st.write(f"Attempt {i+1}: {note_data}")
                                                result = supabase.table("InjuryNote").insert(note_data).execute()
                                                st.write(f"Success with attempt {i+1}")
                                                success = True
                                                break
                                            except Exception as attempt_error:
                                                st.write(f"Attempt {i+1} failed: {str(attempt_error)}")
                                                continue
                                        
                                        if success:
                                            st.success("✅ Note added successfully!")
                                            st.session_state.adding_note_to_injury = None
                                            st.rerun()
                                        else:
                                            st.error("❌ All insertion attempts failed")
                                            
                                    except Exception as schema_error:
                                        st.error(f"❌ Schema check failed: {str(schema_error)}")
                                else:
                                    st.error("❌ Could not find injury record. Please try refreshing the page.")
                                    
                            except Exception as e:
                                st.error(f"❌ Error adding note: {str(e)}")
                        else:
                            st.warning("⚠️ Note message is required")
                    
                    if cancel_note:
                        st.session_state.adding_note_to_injury = None
                        st.rerun()

        # Display injury notes if any exist
        elif player_notes:
            st.subheader("📝 Injury Notes")
            notes_df = df(player_notes)
            
            display_columns = ['InjuryNoteDate', 'OSIICS_Diagnosis', 'InjuryNoteMessage']
            available_columns = [col for col in display_columns if col in notes_df.columns]
            
            if available_columns:
                display_df = notes_df[available_columns]
                st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Show message if no injury data
        if not player_injuries and not player_notes and not st.session_state.adding_note_to_injury:
            st.info("No injury records found for this player.")