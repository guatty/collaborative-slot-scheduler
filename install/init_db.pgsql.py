import psycopg2
import os
con = psycopg2.connect(os.environ["DATABASE_URL"])

UNIQUE_CLASS_BATCH_ID = os.environ["UNIQUE_CLASS_BATCH_ID"]
DATA_TO_IMPORT_PATH = os.environ["DATA_TO_IMPORT_PATH"]

cur = con.cursor()

# cur.execute('''DROP SCHEMA public CASCADE;''')
cur.execute('''CREATE SCHEMA public;''')
cur.execute('''GRANT ALL ON SCHEMA public TO postgres;''')
cur.execute('''GRANT ALL ON SCHEMA public TO public;''')
con.commit()

### CONST like block

cur.execute('''CREATE TABLE "class_states" (
	"meaning"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("meaning")
);''')
cur.execute('''INSERT INTO "class_states" ("meaning") VALUES ('planned');''')
cur.execute('''INSERT INTO "class_states" ("meaning") VALUES ('cancelled');''')
cur.execute('''INSERT INTO "class_states" ("meaning") VALUES ('provided_will_transcribe');''')
cur.execute('''INSERT INTO "class_states" ("meaning") VALUES ('fully_transcripted');''')
cur.execute('''INSERT INTO "class_states" ("meaning") VALUES ('provided_wont_transcribe');''')


cur.execute('''CREATE TABLE "school_years" (
	"school_year"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("school_year")
);''')
cur.execute('''INSERT INTO "school_years" ("school_year") VALUES ('P2_2026');''')
cur.execute('''INSERT INTO "school_years" ("school_year") VALUES ('D1_2025');''')
cur.execute('''INSERT INTO "school_years" ("school_year") VALUES ('P2_2027');''')
cur.execute('''INSERT INTO "school_years" ("school_year") VALUES ('D1_2026');''')


cur.execute('''CREATE TABLE "active_kinds" (
	"kind"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("kind")
);''')
cur.execute('''INSERT INTO "active_kinds" ("kind") VALUES ('actif');''')
cur.execute('''INSERT INTO "active_kinds" ("kind") VALUES ('non_verifie');''')
cur.execute('''INSERT INTO "active_kinds" ("kind") VALUES ('demission');''')
cur.execute('''INSERT INTO "active_kinds" ("kind") VALUES ('mail_verifie');''')

cur.execute('''CREATE TABLE "timeslot_kinds" (
	"timeslot_kind"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("timeslot_kind")
);''')
cur.execute('''INSERT INTO "timeslot_kinds" ("timeslot_kind") VALUES ('scribe');''')
cur.execute('''INSERT INTO "timeslot_kinds" ("timeslot_kind") VALUES ('proofread');''')
cur.execute('''INSERT INTO "timeslot_kinds" ("timeslot_kind") VALUES ('edition');''')


cur.execute('''CREATE TABLE "planning_value_kinds" (
	"planning_value_kind"	TEXT NOT NULL UNIQUE,
	"datatype"	TEXT NOT NULL,
	PRIMARY KEY("planning_value_kind")
);''')
cur.execute('''INSERT INTO "planning_value_kinds" ("planning_value_kind", "datatype") VALUES ('date_time', 'TIMESTAMP');''')
cur.execute('''INSERT INTO "planning_value_kinds" ("planning_value_kind", "datatype") VALUES ('amphi', 'TEXT');''')
cur.execute('''INSERT INTO "planning_value_kinds" ("planning_value_kind", "datatype") VALUES ('intitule', 'TEXT');''')
cur.execute('''INSERT INTO "planning_value_kinds" ("planning_value_kind", "datatype") VALUES ('ens', 'TEXT');''')
cur.execute('''INSERT INTO "planning_value_kinds" ("planning_value_kind", "datatype") VALUES ('duree_sec', 'INTEGER');''')
cur.execute('''INSERT INTO "planning_value_kinds" ("planning_value_kind", "datatype") VALUES ('categorie', 'course_category');''')
cur.execute('''INSERT INTO "planning_value_kinds" ("planning_value_kind", "datatype") VALUES ('h_type', 'course_type');''')
cur.execute('''INSERT INTO "planning_value_kinds" ("planning_value_kind", "datatype") VALUES ('class_state', 'class_state');''')

cur.execute('''CREATE TABLE "right_groups" (
	"right_group"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("right_group")
);''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('presidence_P2');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('recrutement_P2');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('edition_P2');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('planning_P2');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('membre_P2');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('presidence_D1');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('recrutement_D1');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('edition_D1');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('planning_D1');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('membre_D1');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('a_valider_P2');''')
cur.execute('''INSERT INTO "right_groups" ("right_group") VALUES ('a_valider_D1');''')



cur.execute('''CREATE TABLE "users" (
	"id"	SERIAL NOT NULL UNIQUE,
	"firstname"	TEXT NOT NULL,
	"lastname"	TEXT NOT NULL,
	"mail"	TEXT NOT NULL UNIQUE,
	"password"	TEXT NOT NULL,
	"facebook"	TEXT,
	"discord"	TEXT,
	"school_year"	TEXT NOT NULL,
	"right_group"	TEXT NOT NULL,
	"active_kind"	TEXT NOT NULL,
	"contribution_p2"	TEXT,
	"notifications"	TEXT DEFAULT ';',
	"settings"	TEXT DEFAULT ';',
	"update_date"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" ),
	FOREIGN KEY("school_year") REFERENCES "school_years"("school_year"),
	FOREIGN KEY("right_group") REFERENCES "right_groups"("right_group"),
	FOREIGN KEY("active_kind") REFERENCES "active_kinds"("kind")
);''')

### end of const like block



### Admin Planning inputed block

cur.execute('''CREATE TABLE "classes_list" (
	"id"	SERIAL NOT NULL UNIQUE,
	"class_state"	TEXT NOT NULL,
	"school_year"	TEXT NOT NULL,
	PRIMARY KEY("id" ),
	FOREIGN KEY("class_state") REFERENCES "class_states"("meaning"),
	FOREIGN KEY("school_year") REFERENCES "school_years"("school_year")
);
''')


cur.execute('''CREATE TABLE "planning_updates" (
	"id"	SERIAL NOT NULL,
	"creation_date"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"user"	INTEGER,
	"new_value"	TEXT,
	"old_value"	TEXT,
	"reason"	TEXT,
	"value_kind"	TEXT NOT NULL,
	"class_id"	INTEGER NOT NULL,
	PRIMARY KEY("id" ),
	FOREIGN KEY("user") REFERENCES "users"("id"),
	FOREIGN KEY("class_id") REFERENCES "classes_list"("id"),
	FOREIGN KEY("value_kind") REFERENCES "planning_value_kinds"("planning_value_kind")
);''')



### End of Admin Planning inputed block



### User inputed block


cur.execute('''INSERT INTO "users" ("firstname","lastname","mail","password","school_year","right_group","active_kind","update_date") VALUES 
            ('nobody','nobody','nobody@apecs.ml','','P2_2026','membre_P2','non_verifie','2021-06-20 12:34:30')
            ;''')


cur.execute('''CREATE TABLE "assigned_timeslots" (
	"id"	SERIAL NOT NULL,
	"creation_date"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"user_assigned"	INTEGER,
	"user_modif"	INTEGER,
	"reason"	TEXT,
	"timestamp_start"	INTEGER NOT NULL,
	"timestamp_end"	INTEGER NOT NULL,
	"class_id"	INTEGER NOT NULL,
	"timeslot_kind"	TEXT NOT NULL,
	PRIMARY KEY("id" ),
	FOREIGN KEY("user_assigned") REFERENCES "users"("id"),
	FOREIGN KEY("user_modif") REFERENCES "users"("id"),
	FOREIGN KEY("timeslot_kind") REFERENCES "timeslot_kinds"("timeslot_kind"),
	FOREIGN KEY("class_id") REFERENCES "classes_list"("id")
);''')


# ### End of User inputed block



# VUE [ planning_now ]
# - planning_updates
# id -> classes_list
# date_time
# amphi
# intitule
# ens
# duree_sec
# categorie
# h_type
# etat
# class_state -> class_states


# VUE [ transcription_status ]
# - assigned_timeslots
# id
# class_id -> classes_list
# time_start
# time_stop
# scribed
# proofread
# drive

import json
import dateparser
from tqdm import tqdm
from datetime import timezone

with open(DATA_TO_IMPORT_PATH, 'r') as f:
	db = json.load(f)['planning']
	for h in tqdm(db):
		cur.execute('''INSERT INTO "classes_list" ("class_state","school_year") VALUES (%s,%s) RETURNING id;''', ('planned', UNIQUE_CLASS_BATCH_ID))
		class_id = cur.fetchone()[0]
		d=dateparser.parse(h['h_date'] + ' ' + h['h_debut'])
		f=dateparser.parse(h['h_date'] + ' ' + h['h_fin'])
		h_date_time = int(d.replace(tzinfo=timezone.utc).timestamp())
		duree_sec = int((f - d).total_seconds())
  
		cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (2,%s,NULL,%s,'date_time',%s);''', (str(h_date_time), 'import planning ' + UNIQUE_CLASS_BATCH_ID, class_id))
		if h['amphi'] is not None and h['amphi'] != '':
			cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (2,%s,NULL,%s,'amphi',%s);''', (h['amphi'], 'import planning ' + UNIQUE_CLASS_BATCH_ID, class_id))
		cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (2,%s,NULL,%s,'intitule',%s);''', (h['intitule'], 'import planning ' + UNIQUE_CLASS_BATCH_ID, class_id))
		if h['ens'] is not None and h['ens'] != '':
			cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (2,%s,NULL,%s,'ens',%s);''', (h['ens'], 'import planning ' + UNIQUE_CLASS_BATCH_ID, class_id))
		cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (2,%s,NULL,%s,'duree_sec',%s);''', (str(duree_sec), 'import planning ' + UNIQUE_CLASS_BATCH_ID, class_id))
		cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (2,%s,NULL,%s,'categorie',%s);''', (h['categorie'], 'import planning ' + UNIQUE_CLASS_BATCH_ID, class_id))
		cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (2,%s,NULL,%s,'h_type',%s);''', (h['h_type'], 'import planning ' + UNIQUE_CLASS_BATCH_ID, class_id))

cur.execute('''CREATE or replace FUNCTION associated_timeslots_boolean (hclass_id INT)
	RETURNS TABLE (j json) AS
	$$
	BEGIN
		RETURN QUERY
	SELECT json_agg(to_json(d)) from (
		SELECT
			timestamp_start s_begin, 
			timestamp_end s_end, 
			class_id,  
			COALESCE(max(case when timeslot_kind = 'scribe' then user_assigned end)::boolean, false) scribe_prise,
			COALESCE(max(case when timeslot_kind = 'proofread' then user_assigned end)::boolean, false) relecture_prise, 
			COALESCE(max(case when timeslot_kind = 'edition' then user_assigned end)::boolean, false) edition_prise,
			max(case when timeslot_kind = 'edition' then started_date end) edition_started,
			max(case when timeslot_kind = 'edition' then finished_date end) edition_finished,
			max(case when timeslot_kind = 'scribe' then started_date end) scribe_started,
			max(case when timeslot_kind = 'scribe' then finished_date end) scribe_finished,
			max(case when timeslot_kind = 'proofread' then started_date end) relecture_started,
			max(case when timeslot_kind = 'proofread' then finished_date end) relecture_finished
		FROM   assigned_timeslots ats RIGHT JOIN (
		SELECT   MAX(id) mid
		from assigned_timeslots 
		where class_id=hclass_id
		group by timestamp_start, timestamp_end, class_id, timeslot_kind
		) latest 
		on ats.id=latest.mid
		where user_assigned <> 3 and user_assigned <> 4
		group by timestamp_start, timestamp_end, class_id
		order by timestamp_start asc
	) as d;
	END;
	$$ LANGUAGE plpgsql;
  ''')

cur.execute('''CREATE or replace FUNCTION user_info (user_id INT)
	RETURNS TABLE (j json) AS
	$$
	BEGIN
		RETURN QUERY
	SELECT to_json(d) from (
		SELECT
			firstname,
			lastname
			from users
			where id=user_id
	) as d;
	END;
	$$ LANGUAGE plpgsql;
  ''')

cur.execute('''CREATE or replace FUNCTION associated_timeslots_user_id (hclass_id INT)
	RETURNS TABLE (j json) AS
	$$
	BEGIN
		RETURN QUERY
	SELECT json_agg(to_json(d)) from (
		SELECT
			timestamp_start s_begin, 
			timestamp_end s_end, 
			class_id,  
   			user_info(max(case when timeslot_kind = 'scribe' then user_assigned end)) scribe,
			user_info(max(case when timeslot_kind = 'proofread' then user_assigned end)) proofread,
			user_info(max(case when timeslot_kind = 'edition' then user_assigned end)) edition,
			max(case when timeslot_kind = 'edition' then started_date end) edition_started,
			max(case when timeslot_kind = 'edition' then finished_date end) edition_finished,
			max(case when timeslot_kind = 'scribe' then started_date end) scribe_started,
			max(case when timeslot_kind = 'scribe' then finished_date end) scribe_finished,
			max(case when timeslot_kind = 'proofread' then started_date end) relecture_started,
			max(case when timeslot_kind = 'proofread' then finished_date end) relecture_finished
		FROM   assigned_timeslots ats RIGHT JOIN (
		SELECT   MAX(id) mid
		from assigned_timeslots 
		where class_id=hclass_id
		group by timestamp_start, timestamp_end, class_id, timeslot_kind
		) latest 
		on ats.id=latest.mid
		where user_assigned <> 3 and user_assigned <> 4
		group by timestamp_start, timestamp_end, class_id
		order by timestamp_start asc
	) as d;
	END;
	$$ LANGUAGE plpgsql;
  ''')

cur.execute('''CREATE or replace FUNCTION contrib_assigned_ts (user_id INT)
	RETURNS TABLE (j json) AS
	$$
	BEGIN
		RETURN QUERY
	select (SELECT to_json(d) from (
		SELECT
			count(scribe) h_scribe,
			count(proofread) h_proofread
		FROM   assigned_timeslots ats left JOIN (
		SELECT   MAX(id) mid, 
			max(case when timeslot_kind = 'scribe' then user_assigned end) scribe,
			max(case when timeslot_kind = 'proofread' then user_assigned end) proofread 
		from assigned_timeslots 
		group by timestamp_start, timestamp_end, class_id, timeslot_kind
		) latest 
		on ats.id=latest.mid
		where user_assigned = user_id
		group by user_assigned
	) as d);
	END;
	$$ LANGUAGE plpgsql;
  ''')





con.commit()

con.close()
