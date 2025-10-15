```sql
-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.athlete (
  athlete_id uuid NOT NULL DEFAULT gen_random_uuid(),
  athlete_yob integer NOT NULL,
  athlete_name character varying NOT NULL,
  athlete_details jsonb NOT NULL,
  CONSTRAINT athlete_pkey PRIMARY KEY (athlete_id)
);
CREATE TABLE public.injury (
  injury_id uuid NOT NULL DEFAULT gen_random_uuid(),
  athlete_id uuid NOT NULL,
  ossics_code character varying NOT NULL,
  moo_id uuid,
  moi_id uuid,
  start_date date NOT NULL DEFAULT CURRENT_DATE,
  rpt date,
  rpg date,
  ftdg date,
  CONSTRAINT injury_pkey PRIMARY KEY (injury_id),
  CONSTRAINT injury_athlete_id_fkey FOREIGN KEY (athlete_id) REFERENCES public.athlete(athlete_id),
  CONSTRAINT injury_ossics_code_fkey FOREIGN KEY (ossics_code) REFERENCES public.osiics(osiics_code),
  CONSTRAINT injury_moo_id_fkey FOREIGN KEY (moo_id) REFERENCES public.mode_of_onset(moo_id),
  CONSTRAINT injury_moi_id_fkey FOREIGN KEY (moi_id) REFERENCES public.mechanism_of_injury(moi_id)
);
CREATE TABLE public.injury_notes (
  note_id uuid NOT NULL DEFAULT gen_random_uuid(),
  injury_id uuid,
  note_content character varying NOT NULL,
  note_created_at date NOT NULL DEFAULT CURRENT_DATE,
  CONSTRAINT injury_notes_pkey PRIMARY KEY (note_id),
  CONSTRAINT injury_notes_injury_id_fkey FOREIGN KEY (injury_id) REFERENCES public.injury(injury_id)
);
CREATE TABLE public.mechanism_of_injury (
  moi_id uuid NOT NULL DEFAULT gen_random_uuid(),
  injury character varying NOT NULL,
  type_of_contact character varying NOT NULL,
  description character varying NOT NULL,
  CONSTRAINT mechanism_of_injury_pkey PRIMARY KEY (moi_id)
);
CREATE TABLE public.mode_of_onset (
  moo_id uuid NOT NULL DEFAULT gen_random_uuid(),
  mechanism character varying NOT NULL,
  presentaion character varying NOT NULL,
  CONSTRAINT mode_of_onset_pkey PRIMARY KEY (moo_id)
);
CREATE TABLE public.osiics (
  osiics_code character varying NOT NULL,
  osiics_version character varying NOT NULL,
  diagnosis character varying NOT NULL,
  bodypart character varying NOT NULL,
  tissue_type character varying,
  pathology_type character varying,
  medical_system character varying,
  etiology character varying,
  CONSTRAINT osiics_pkey PRIMARY KEY (osiics_code)
);
```