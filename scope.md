Injury Logging System – MVP Scoping Document

Date: 11 September 2025
Prepared by: [Daniel Dickerson]

⸻

1. Problem Statement

Currently, injury data is captured inconsistently, making it difficult to analyze trends, track recovery progress, and standardize reporting across the academy. This leads to inefficiencies in communication and limited ability to use injury data for performance and prevention insights.

The MVP aims to provide a standardized digital platform for physios to record and manage injuries in a structured, centralized database.

⸻

2. Goals of MVP
	•	Enable physios to log new injuries in a consistent, standardized format.
	•	Provide the ability to update recovery timeframes as the athlete progresses.
	•	Allow physios to view each player’s injury history in one place.
	•	Allow notes to be attached to injuries for context and details.
	•	Ensure data aligns with the existing injury classification schema (e.g., OSICS, mode of onset).

⸻

3. Primary Users
	•	Physios (Phase 1 MVP): Record and manage injury data.
	•	Future users (Post-MVP): Strength and conditioning coaches, who will reference recovery plans and injury histories for training decisions.

⸻

4. Scope of MVP

Functional Requirements
	1.	Injury Logging
	•	Form to input new injury details with required fields from the existing schema (e.g., OSICS classification, mode of onset, body part, severity, date).
	2.	Recovery Updates
	•	Ability to update expected return-to-play/recovery timeframe for an existing injury record.
	3.	Player History
	•	Ability to view historical injuries per player.
	•	Search or filter by player name.
	4.	Notes
	•	Attach and view free-text notes against each injury record.

Non-Functional Requirements
	•	Platform: Web-based, built in Streamlit.
	•	Database: Aligned with existing injury schema (enforced fields).
	•	Security: Basic authentication for physios (Supabase or equivalent).
	•	Timeline: Deliver functional MVP by end of September 2025.

⸻

5. Out of Scope (Post-MVP)
	•	Templated recovery plans linked to injuries.
	•	Automated communication (e.g., sending athletes daily training schedules via SMS).
	•	Advanced analytics and visualization dashboards.
	•	Integration with performance data systems.
	•	Mobile app or mobile-first design (initial focus on desktop web).

⸻

6. Constraints
	•	Team: 2 developers (interns).
	•	Time: ~3 weeks to deliver MVP.
	•	Tools: Streamlit for UI/dashboard, existing DB schema for storage, Supabase for auth and db.

⸻

7. Next Steps
	1.	Confirm database schema and enforce required fields in injury logging form.
	2.	Build basic Streamlit dashboard:
	•	New injury entry form.
	•	Player history view.
	•	Recovery update workflow.
	3.	Implement authentication layer (Supabase auth).
	4.	Test workflows with physios for usability feedback.
	5.	Iterate for MVP release before end of September.
