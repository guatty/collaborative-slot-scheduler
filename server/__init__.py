from flask import Flask, jsonify, request, g, current_app, redirect
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
import time
import jwt
from datetime import datetime, timedelta
from functools import wraps
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To
from urllib.parse import quote as upquote
from functools import reduce
import hashlib
import os
import logging

from dotenv import load_dotenv

load_dotenv()

# configuration
if "DEBUG" in os.environ:
    DEBUG = True

USER_REGISTERING_OPEN = "USER_REGISTERING_OPEN" in os.environ


app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(
    SECRET_KEY=os.environ['SECRET_API_KEY']
)


# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})
def get_conn():
    if 'db' in g:
        try:
            cur = g.db.cursor()
            cur.execute('SELECT 1;')
            return g.db
        except psycopg2.OperationalError:
            close_conn(None)
            logging.error("Connection error. Retrying in 2s..")
            time.sleep(2)
            return get_conn()        
    else:
        g.db = psycopg2.connect(os.getenv('DATABASE_URL'))
        return g.db

@app.teardown_appcontext
def close_conn(e):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def dumb_proof(password):
    """ sigh.... """
    return password.strip()

def hash_pwd(usermail, pwd):
    salt = current_app.config['SECRET_KEY'] + usermail.lower()
    return hashlib.pbkdf2_hmac('sha256', dumb_proof(pwd).encode('utf-8'), salt, 100000)

def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Invalid token. Registration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }

        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user = get_user_by_mail(data['sub'])
            if user is None:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401 # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError) as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            # log(message)
            return jsonify(invalid_msg), 401

    return _verify


def token_required_even_expired(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Invalid token. Registration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }

        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], leeway=31104000, algorithms=["HS256"])
            user = get_user_by_mail(data['sub'])
            if user is None:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify(expired_msg), 401 # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError) as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            # log(message)
            return jsonify(invalid_msg), 401

    return _verify

def fill_until_end_timestamp(expandedTS, end_ts, init_time_cursor, curr_slot_id):
    i = curr_slot_id
    curr_time_cursor = init_time_cursor
    while end_ts > curr_time_cursor:
        # Pas de scribe ni de relecteur inscrit : on crée le créneau pour permettre de s'y inscrire
        # on itère par tranche d'une heure
        ts = {'slot_id': i}
        ts['s_begin'] = curr_time_cursor
        if end_ts - curr_time_cursor <= 7000:
            ts['s_end'] = end_ts
        else:
            ts['s_end'] = ts['s_begin'] + 3600
        ts['scribe_prise'] = False
        ts['chercheScribe'] = not ts['scribe_prise']
        ts['relecture_prise'] = False
        ts['chercheRelecture'] = not ts['relecture_prise']
        curr_time_cursor = ts['s_end']
        i+=1
        expandedTS.append(ts)
    return expandedTS, i, curr_time_cursor

def expandWithSuscribableTimeSlots(hclass):
    class_length = hclass['duree_sec']
    assignedTimeslots = hclass['timeslots']
    if assignedTimeslots is None:
        hclass['timeslots'], _, _ = fill_until_end_timestamp([], class_length, 0, 1)
        return None
    expandedTS = []
    curr_time_cursor = 0
    i=0
    for ats in assignedTimeslots:
        i+=1
        ats_start = ats['s_begin']
        ats_end = ats['s_end']

        expandedTS, i, curr_time_cursor = fill_until_end_timestamp(expandedTS, ats_start, curr_time_cursor, i)

        assert ats_start == curr_time_cursor
        # Un scribe/relecteur s'est inscrit, pas besoin d'expand
        ats['slot_id'] = i
        ats['chercheScribe'] = 'scribe' in ats or not ats['scribe_prise']
        ats['chercheRelecture'] = 'proofread' in ats or not ats['relecture_prise']
        expandedTS.append(ats)
        curr_time_cursor = ats_end

        
    expandedTS, _, _ = fill_until_end_timestamp(expandedTS, class_length, curr_time_cursor, i+1)
    
    hclass['timeslots'] = expandedTS

def willHclassBeRoneo(hclass):
    '''
    QUESTION :
        UrgVit -> 1 séance / groupe (20) : 1er le 29 octobre 2021
        CUESIM -> 3 séances / groupe (20 & 5*10 & 5*10) : 1er le 2 février 2022
        ECOS -> 1 séance / groupe (7) : 1er le 6 janvier 2022
        AFGSU -> 2 séances / groupe (30) : 1er le 7 décembre 2021
    '''
    if hclass['categorie'] in ['MB', 'UE1', 'UE2', 'UE3', 'UE4', 'UE5', 'UE6', 'UE7', 'UE8:Biostat', 'UE8:LCA']: # D1
        return True
    elif hclass['categorie'] in ['UE1', 'UE2', 'UE3', 'UE4', 'UE5', 'UE6', 'UE7', 'UE8', 'UE9', 'UE10', 'UE11', 'UE12', 'UE13', 'UE14']: # P2
        return True
    else:
        return False


def fill_blanks_in_timeslots(hclass):
    if willHclassBeRoneo(hclass):
        expandWithSuscribableTimeSlots(hclass)
    else:
        hclass['nonRetranscritRaison'] = "Non retranscrit par l'APECS"
    return hclass

def reduce_to_weeks(days):
    weeks = []
    curr_week_number = -1

    for day in days:
        if day['week_number'] != curr_week_number:
            curr_week_number = day['week_number']
            weeks.append({
                'week_number': curr_week_number,
                'week_days' : []
            })
        weeks[-1]['week_days'].append(day)
    return weeks


def reduce_to_days(hclasses):
    days = []
    curr_day = -1

    for hclass in hclasses:
        if hclass['h_date'] != curr_day:
            curr_day = hclass['h_date']
            days.append({
                'h_date': curr_day,
                'day_hclasses' : [],
                'week_number': hclass['week_number']
            })
        days[-1]['day_hclasses'].append(hclass)
    return days

def addKVToDictInplace(d, key, value):
    d[key] = value
    return d

def expand_and_reduce(hclasses):
    list(map(lambda x: fill_blanks_in_timeslots(x), hclasses))
    return reduce_to_weeks(reduce_to_days(hclasses))

def from_db_d1_for(user_id):
    cur = get_conn().cursor()

    cur.execute('''SELECT json_agg(to_json(d)) from (
		SELECT
			s.class_id,
			extract('week' from to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date) as week_number,
			to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date h_date_nonchar,
			to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer) date_time,
			TO_CHAR(to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date, 'YYYY-MM-DD') h_date,
			(SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer h_debut,
            TO_CHAR(to_timestamp(((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer + (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer))::time, 'HH24hMI') h_fin,
			EXTRACT(epoch FROM((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) || ' second')::interval) duree_sec,
			(SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'amphi'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) amphi,
			(SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'intitule'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) intitule,
			(SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'ens'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) ens,
			(SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'categorie'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) categorie,
			(SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'h_type'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) h_type,
			associated_timeslots_user_id(s.class_id) timeslots
		from planning_updates s
            right join (
		SELECT
			timestamp_start s_begin, 
			timestamp_end s_end, 
			class_id,  
			max(case when timeslot_kind = 'scribe' then user_assigned end) scribe,
			max(case when timeslot_kind = 'proofread' then user_assigned end) proofread 
		FROM   assigned_timeslots ats RIGHT JOIN (
		SELECT   MAX(id) mid
		from assigned_timeslots 
		group by timestamp_start, timestamp_end, class_id, timeslot_kind
		) latest 
		on ats.id=latest.mid
		where user_assigned <> 3 and user_assigned <> 4 and user_assigned = %s
		group by timestamp_start, timestamp_end, class_id
		order by timestamp_start asc) uts on s.class_id=uts.class_id
	group by s.class_id
	order by date_time asc
        ) as d;''', (user_id,))
    rows = cur.fetchall()[0][0]
    if rows is None:
        return []
    planning = expand_and_reduce(rows)
    return planning

def from_db_d1_class(class_id):
    cur = get_conn().cursor()

    cur.execute('''SELECT to_json(d) from (
            SELECT
                s.class_id,
                extract('week' from to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date) as week_number,
                to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date h_date_nonchar,
                to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer) date_time,
                TO_CHAR(to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date, 'YYYY-MM-DD') h_date,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer h_debut,
                TO_CHAR(to_timestamp(((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer + (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer))::time, 'HH24hMI') h_fin,
                EXTRACT(epoch FROM((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) || ' second')::interval) duree_sec,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'amphi'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) amphi,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'intitule'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) intitule,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'ens'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) ens,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'categorie'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) categorie,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'h_type'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) h_type,
                associated_timeslots_user_id(s.class_id) timeslots
            from planning_updates s
            left join (
		SELECT
			timestamp_start s_begin, 
			timestamp_end s_end, 
			class_id,  
			max(case when timeslot_kind = 'scribe' then user_assigned end) scribe,
			max(case when timeslot_kind = 'proofread' then user_assigned end) proofread 
		FROM   assigned_timeslots ats RIGHT JOIN (
		SELECT   MAX(id) mid
		from assigned_timeslots 
		where class_id=%s
		group by timestamp_start, timestamp_end, class_id, timeslot_kind
		) latest 
		on ats.id=latest.mid
		where user_assigned <> 3 and user_assigned <> 4 and class_id=%s
		group by timestamp_start, timestamp_end, class_id
		order by timestamp_start asc) uts on s.class_id=uts.class_id
            where s.class_id=%s
		            group by s.class_id
            order by date_time asc
        ) as d;''', (class_id,class_id,class_id))
    row = cur.fetchone()[0]
    return row

def is_slot_taken(class_id, ts_start, ts_end, timeslot_kind):
    cur = get_conn().cursor()
    cur.execute('''SELECT to_json(d) from (
        		SELECT
			timestamp_start s_begin, 
			timestamp_end s_end, 
			class_id,  
			COALESCE(max(case when timeslot_kind = 'scribe' then user_assigned end)::boolean, false) scribe_prise,
			COALESCE(max(case when timeslot_kind = 'proofread' then user_assigned end)::boolean, false) relecture_prise, 
			COALESCE(max(case when timeslot_kind = 'edition' then user_assigned end)::boolean, false) edition_prise 
            FROM   assigned_timeslots ats RIGHT JOIN (
            SELECT   MAX(id) mid
            from assigned_timeslots 
            where class_id=%s
            group by timestamp_start, timestamp_end, class_id, timeslot_kind
            ) latest 
            on ats.id=latest.mid
            where user_assigned <> 3 and user_assigned <> 4 and (timestamp_start=%s or timestamp_end=%s)
            group by timestamp_start, timestamp_end, class_id
            order by timestamp_start asc
        ) as d;''', (class_id, ts_start, ts_end))
    row = cur.fetchone()
    if row is None:
        return False
    else:
        dediff = { 
                    'scribe': 'scribe_prise',
                    'relecture': 'relecture_prise',
                    'edition': 'edition_prise'
                  }
        return row[0][dediff[timeslot_kind]]

def hasPlanningRights(user):
    db_user = get_user_by_id(user['id'])
    return db_user["right_group"] in ["presidence_P2", "planning_P2", "presidence_D1", "planning_D1"]

def isAllowedToCancelSlot(user, class_id, ts_start, ts_end, timeslot_kind):
    slot_info = is_slot_taken(class_id, ts_start, ts_end, timeslot_kind)
    cur = get_conn().cursor()
    cur.execute('''SELECT to_json(d) from (
        		SELECT
			timestamp_start s_begin, 
			timestamp_end s_end, 
			class_id,  
			COALESCE(max(case when timeslot_kind = 'scribe' then user_assigned end), NULL) scribe_prise,
			COALESCE(max(case when timeslot_kind = 'proofread' then user_assigned end), NULL) relecture_prise, 
			COALESCE(max(case when timeslot_kind = 'edition' then user_assigned end), NULL) edition_prise 
            FROM   assigned_timeslots ats RIGHT JOIN (
            SELECT   MAX(id) mid
            from assigned_timeslots 
            where class_id=%s
            group by timestamp_start, timestamp_end, class_id, timeslot_kind
            ) latest 
            on ats.id=latest.mid
            where user_assigned <> 3 and user_assigned <> 4 and (timestamp_start=%s or timestamp_end=%s)
            group by timestamp_start, timestamp_end, class_id
            order by timestamp_start asc
        ) as d;''', (class_id, ts_start, ts_end))
    row = cur.fetchone()
    if row is None:
        return False
    else:
        dediff = { 
                    'scribe': 'scribe_prise',
                    'relecture': 'relecture_prise',
                    'edition': 'edition_prise'
                  }
        assigned_used_id = row[0][dediff[timeslot_kind]]
        return assigned_used_id == user['id'] or hasPlanningRights(user)


@app.route('/planningD1gestion', methods=['GET', 'POST'])
def planningD1gestion():
    return whole_planning(withNames=True, school_year="D1_2025")

@app.route('/planningP2', methods=['GET', 'POST'])
def planningP2():
    return whole_planning(withNames=False, school_year="P2_2026")

@app.route('/planningP2gestion', methods=['GET', 'POST'])
def planningP2gestion():
    return whole_planning(withNames=True, school_year="P2_2026")

@app.route('/rollingPlanningP2', methods=['GET'])
def rollingPlanningP2():
    cur = get_conn().cursor()

    cur.execute('''SELECT json_agg(to_json(d)) from (
            select * from (SELECT
                class_id,
                extract('week' from to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date) as week_number,
                to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date h_date_nonchar,
                to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer) date_time,
                TO_CHAR(to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date, 'YYYY-MM-DD') h_date,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer h_debut,
                TO_CHAR(to_timestamp(((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer + (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer))::time, 'HH24hMI') h_fin,
                EXTRACT(epoch FROM((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) || ' second')::interval) duree_sec,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'amphi'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) amphi,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'intitule'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) intitule,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'ens'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) ens,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'categorie'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) categorie,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'h_type'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) h_type,
                associated_timeslots_user_id(class_id) timeslots
            from planning_updates s
            where class_id in (select id from classes_list where school_year='P2_2026')
            group by class_id
            order by date_time asc) as t
            where t.h_date_nonchar > CURRENT_DATE -6 limit 20
        ) as d;''')
    rows = cur.fetchall()[0][0]
    if rows is None:
        return jsonify([])
    planning = expand_and_reduce(rows)
    return jsonify(planning)

@app.route('/rollingPlanningD1', methods=['GET'])
def rollingPlanningD1():
    cur = get_conn().cursor()

    cur.execute('''SELECT json_agg(to_json(d)) from (
            select * from (SELECT
                class_id,
                extract('week' from to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date) as week_number,
                to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date h_date_nonchar,
                to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer) date_time,
                TO_CHAR(to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date, 'YYYY-MM-DD') h_date,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer h_debut,
                TO_CHAR(to_timestamp(((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer + (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer))::time, 'HH24hMI') h_fin,
                EXTRACT(epoch FROM((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) || ' second')::interval) duree_sec,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'amphi'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) amphi,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'intitule'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) intitule,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'ens'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) ens,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'categorie'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) categorie,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'h_type'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) h_type,
                associated_timeslots_user_id(class_id) timeslots
            from planning_updates s
            where class_id in (select id from classes_list where school_year='D1_2025')
            group by class_id
            order by date_time asc) as t
            where t.h_date_nonchar > CURRENT_DATE -6 limit 20
        ) as d;''')
    rows = cur.fetchall()[0][0]
    if rows is None:
        return jsonify([])
    planning = expand_and_reduce(rows)
    return jsonify(planning)

def partition(list_to_partition, predicate):
    return reduce(lambda matches, remaining: matches[not predicate(remaining)].add(remaining) or matches, list_to_partition, (set(), set()))

@app.route('/planningD1', methods=['GET', 'POST'])
def whole_planning(withNames=False, school_year="D1_2025"):
    data = request.get_json()
    includers_htype = set()
    includers_categorie = set()
    includers = set()
    groups1to12 = set()
    restreintes = set()
    
    if data is not None:
        allowed_values=['StageSemio:T1', 'StageSemio:T2', 'StageSemio:T3', 'TD:JDR:G1', 'TD:JDR:G2', 'TD:JDR:G3', 'TD:JDR:G4', 'ED:Pharmaco', 'TP:AnatomieUE3.1', 'TP:Histologie', 'TP:AnatomieUE5.1', 'TP:AnatomieUE5.2', 'TP:AnatomieUE6.1', 'TP:Physiologie', 'ED:Genetique.1', 'TP:BioSens.1', 'TP:BioSens.2', 'UE1', 'UE2', 'UE3', 'UE4', 'UE5', 'UE6', 'UE7', 'UE8:Biostat', 'UE8:LCA', 'AFGSU', 'CasClin', 'CC', 'CUESIM', 'ECOS', 'examen', 'Pres', 'UrgVit', 'SSES', 'MB', 'MI', 'Ophtalmologie', 'semio', 'StageSemio', 'TP:BioSens.1', 'TP:BioSens.1', ':G1', ':G2', ':G3', ':G4', ':G5', ':G6', ':G7', ':G8', ':G9', ':G10', ':G11', ':G12', 'UE9', 'UE10', 'UE11', 'UE12', 'UE13', 'UE14']
        includers_htype, groups1to12 = partition( {e['h_type'] for e in data if e['h_type'] in allowed_values}, lambda x: x not in [":G1", ":G2", ":G3", ":G4", ":G5", ":G6", ":G7", ":G8", ":G9", ":G10", ":G11", ":G12"])
        includers_categorie = {e['categorie'] for e in data if e['categorie'] in allowed_values and e['h_type']==''}
        includers = includers_htype.union(includers_categorie)
        restreintes = { e['restreinte'] for e in data if 'restreinte' in e and e['restreinte'] in ['CM', 'S1', 'S2', 'FASM1', 'hodiaux'] }    

    restrict_cond = "True"
    if includers != set() or groups1to12 != set() or restreintes != set():
        query_includers = "True"
        query_groups1to12 = "True"
        
        if includers != set():
            query_includers_categorie = "categorie in ({0})".format(', '.join(["'{}'".format(value) for value in includers_categorie])) if includers_categorie != set() else "False"
            query_includers_htype = "h_type ~ '{0}'".format('|'.join(includers_htype)) if includers_htype != set() else "False"
            query_includers = " ( {0} ) or ( {1} ) ".format(query_includers_categorie, query_includers_htype)
            
        if groups1to12 != set():
            query_groups1to12 = "h_type not in ('TD:JDR:G1', 'TD:JDR:G2', 'TD:JDR:G3', 'TD:JDR:G4') and h_type ~ '{0}'".format('|'.join(groups1to12))
           

        restrict_cond = " ( {0} ) and ( {1} ) ".format(query_includers, query_groups1to12)
        if 'CM' in restreintes:
            restrict_cond += " and h_type='CM' "
            restreintes.discard('CM')

        if 'hodiaux' in restreintes:
            restrict_cond += " and DATE(h_date_nonchar) >= CURRENT_DATE "
            restreintes.discard('hodiaux')

        if restreintes != set():
            l = []
            if 'S1' in restreintes:
                l.append(" h_date_nonchar <= '2021-11-18'")
            if 'S2' in restreintes:
                l.append(" h_date_nonchar > '2021-11-18' and h_date_nonchar <= '2022-03-09'")
            if 'FASM1' in restreintes:
                l.append(" h_date_nonchar > '2022-03-09'")
            
            restrict_cond += " AND ( {0} ) ".format(" or ".join(l))
     
    cur = get_conn().cursor()
    cur.execute('''SELECT json_agg(to_json(d)) from (
        SELECT
            class_id,
            extract('week' from to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date) as week_number,
            to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date h_date_nonchar,
            to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer) date_time,
            TO_CHAR(to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date, 'YYYY-MM-DD') h_date,
            (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer h_debut,
            TO_CHAR(to_timestamp(((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer + (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer))::time, 'HH24hMI') h_fin,
            EXTRACT(epoch FROM((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) || ' second')::interval) duree_sec,
            (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'amphi'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) amphi,
            (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'intitule'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) intitule,
            (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'ens'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) ens,
            (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'categorie'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) categorie,
            (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'h_type'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) h_type,
            '''
            + (' associated_timeslots_user_id(class_id) timeslots ' if withNames else ' associated_timeslots_boolean(class_id) timeslots ') +
        '''
        from planning_updates s
        where class_id in (select id from classes_list where school_year=%s)
        group by class_id
        order by date_time asc
    ) as d
    where '''
    + restrict_cond +''';''', (school_year,))

    rows = cur.fetchall()
    if rows[0][0] is None:
        return jsonify([])
    planning = expand_and_reduce(rows[0][0])
    return jsonify(planning)


@app.route('/myPlanning', methods=['GET'])
@token_required
def getMyPlanning(user):
    return jsonify(from_db_d1_for(user['id']))

@app.route('/planningForUserMail', methods=['POST'])
@token_required
def planningForUserMail(user):
    data = request.get_json()
    mail = data['mail']
    return jsonify(from_db_d1_for(get_user_by_mail(mail)))

@app.route('/allmembers', methods=['POST'])
@token_required
def allmembers(user):
    if not hasMembersManagementRights(user):
        return jsonify({'message':"Erreur. Vous n'avez pas le droit d'accéder à ces données personnelles"})

    data = request.get_json()
    

    cur = get_conn().cursor()
    
    cur.execute('''SELECT json_agg(to_json(d)) from (
            SELECT
                firstname,
                lastname,
                mail,
                school_year
            from users 
            where id>=5
            order by firstname asc
        ) as d;''')
    rows = cur.fetchall()[0][0]
    
    if rows is None:
        rows=[]
    
    return jsonify(rows)

@app.route('/membersP2', methods=['POST'])
@token_required
def membersP2(user):
    if not hasMembersManagementRights(user):
        return jsonify({'message':"Erreur. Vous n'avez pas le droit d'accéder à ces données personnelles"})

    data = request.get_json()
    

    cur = get_conn().cursor()
    
    if data['hideinactive']:
        cur.execute('''SELECT json_agg(to_json(d)) from (
                SELECT
                    firstname,
                    lastname,
                    mail,
                    facebook,
                    discord,
                    school_year,
                    right_group,
                    active_kind,
                    contribution_p2,
                    notifications,
                    settings, 
                    contrib_assigned_ts(id) cat
                from users 
                where id>=5 and school_year='P2_2026' and settings not like '%erasmus%' and settings not like '%demission%' 
                order by firstname asc
            ) as d;''')
    else:
        cur.execute('''SELECT json_agg(to_json(d)) from (
                SELECT
                    firstname,
                    lastname,
                    mail,
                    facebook,
                    discord,
                    school_year,
                    right_group,
                    active_kind,
                    contribution_p2,
                    notifications,
                    settings, 
                    contrib_assigned_ts(id) cat
                from users 
                where id>=5 and school_year='P2_2026'
                order by firstname asc
            ) as d;''')
    rows = cur.fetchall()[0][0]
    
    if rows is None:
        rows=[]
    
    return jsonify(rows)


@app.route('/membersD1', methods=['POST'])
@token_required
def membersD1(user):
    if not hasMembersManagementRights(user):
        return jsonify({'message':"Erreur. Vous n'avez pas le droit d'accéder à ces données personnelles"})
    else:
        cur = get_conn().cursor()

    data = request.get_json()

    cur.execute("""SELECT json_agg(to_json(d)) from (
            SELECT
                firstname,
                lastname,
                mail,
                facebook,
                discord,
                school_year,
                right_group,
                active_kind,
                contribution_p2,
                notifications,
                settings, 
                contrib_assigned_ts(id) cat
            from users 
            where id>=5 and school_year='D1_2025' and settings not like '%erasmus%' and settings not like '%demission%' 
            order by firstname asc
        ) as d;""")
    rows = cur.fetchall()[0][0]
    
    for row in rows:
        row['contribution_p2'] = "0:0" # code was scraped, left as is for future implementation
        
    
    return jsonify(rows)
    
@app.route('/confirmCancelCreneauPlanning', methods=['POST'])
@token_required
def confirmCancelCreneauPlanning(user):
    requester_user_id = user['id']
    void_user_id = 3
    data_up = (
        str(void_user_id), 
        str(requester_user_id), 
        str(request.get_json()['reason']), 
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']), 
        str(request.get_json()['class_id']), 
        str({'scribe': 'scribe', 'relecture': 'proofread', 'edition': 'edition'}[request.get_json()['timeslot_kind']])
    )
    
    if hasPlanningRights(user):
        cur = get_conn().cursor()
        cur.execute('''INSERT INTO "assigned_timeslots"
            ("user_assigned", "user_modif", "reason", "timestamp_start", "timestamp_end", "class_id", "timeslot_kind")
            VALUES (%s, %s, %s, %s, %s, %s, %s);''', data_up)
        get_conn().commit()
        # todo: add proper check commit async in front
        return jsonify({'message':"Votre choix de créneau a bien été enregistré !"})
    else:
        return jsonify({'message':"Erreur inconnue. Veuiller fermer et rouvrir le planning."})

@app.route('/addClass', methods=['POST'])
@token_required
def addClass(user):
    requester_user_id = user['id']
    uid = str(requester_user_id)
    reason = str(request.get_json()['reason'])
    amphi = str(request.get_json()['amphi'])
    ens = str(request.get_json()['ens'])
    h_date_time = str(request.get_json()['date_time'])
    duree_sec = str(request.get_json()['duree_sec'])
    intitule = str(request.get_json()['intitule'])
    # categorie = str(request.get_json()['categorie']) # TODO: add in form
    categorie = 'UE' + str(request.get_json()['num_ue'])
    # h_type = str(request.get_json()['h_type']) # TODO: add in form
    h_type = "CM"
    hardcoded_shool_year = "P2_2026"

    try:
        cur = get_conn().cursor()
        cur.execute('''INSERT INTO "classes_list" ("class_state","school_year") VALUES (%s,%s) RETURNING id;''', ('planned', hardcoded_shool_year))
        class_id = cur.fetchone()[0]
        cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (%s,%s,NULL,%s,'date_time',%s);''', (uid, str(h_date_time), reason, class_id))
        if amphi is not None and amphi != '':
            cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (%s,%s,NULL,%s,'amphi',%s);''', (uid, amphi, reason, class_id))
        cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (%s,%s,NULL,%s,'intitule',%s);''', (uid, intitule, reason, class_id))
        if ens is not None and ens != '':
            cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (%s,%s,NULL,%s,'ens',%s);''', (uid, ens, reason, class_id))
        cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (%s,%s,NULL,%s,'duree_sec',%s);''', (uid, str(duree_sec), reason, class_id))
        cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (%s,%s,NULL,%s,'categorie',%s);''', (uid, categorie, reason, class_id))
        cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (%s,%s,NULL,%s,'h_type',%s);''', (uid, h_type, reason, class_id))
        get_conn().commit()
        return jsonify({'message':"Nouveau cours enregistré !"})
    except Exception as e:
        logging.error(e)
        return jsonify({'message':"Erreur T_T ..."})

@app.route('/editClass', methods=['POST'])
@token_required
def editClass(user):
    uid = user['id']
    class_id = int(request.get_json()['class_id'])
    reason = str(request.get_json()['reason'])
    new_values = {"amphi": request.get_json()['amphi'], "ens": request.get_json()['ens'], "date_time": request.get_json()['date_time'], "duree_sec": int(request.get_json()['duree_sec']), "intitule": request.get_json()['intitule']}
    
    cur = get_conn().cursor()
    cur.execute('''SELECT to_json(d) from (SELECT
                class_id,
                extract('week' from to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date) as week_number,
                to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date h_date_nonchar,
                TO_CHAR(to_timestamp((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer)::date, 'YYYY-MM-DD') h_date,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer date_time,
                TO_CHAR(to_timestamp(((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'date_time'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer + (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1)::integer))::time, 'HH24hMI') h_fin,
                EXTRACT(epoch FROM((SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'duree_sec'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) || ' second')::interval) duree_sec,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'amphi'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) amphi,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'intitule'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) intitule,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'ens'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) ens,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'categorie'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) categorie,
                (SELECT new_value FROM planning_updates WHERE new_value IS NOT NULL and value_kind = 'h_type'and class_id=s.class_id ORDER BY creation_date DESC LIMIT 1) h_type
            from planning_updates s
            where class_id=%s
            group by class_id
            order by date_time asc) as d;''', (class_id,))
    old_values = cur.fetchone()[0]

    for key, nv in new_values.items():
        assert key in ['date_time', 'amphi', 'intitule', 'ens', 'duree_sec', 'categorie', 'h_type'], key
        ov = old_values[key]
        if nv != ov:
            cur.execute('''INSERT INTO "planning_updates" ("user","new_value","old_value","reason","value_kind","class_id") VALUES (%s,%s,%s,%s,%s,%s);''', (uid, nv, ov, reason, key, class_id))
            get_conn().commit()

    try:
        return jsonify({'message':"Cours bien modifié !"})
    except Exception as e:
        logging.error(e)
        return jsonify({'message':"Erreur T_T ..."})

@app.route('/assignMemberToSlot', methods=['POST'])
@token_required
def assignMemberToSlot(user):
    assigned_uid = get_user_by_mail(request.get_json()['user_assigned_mail'])['id']
    requester_user_id = user['id']
    data_up = (
        str(assigned_uid), 
        str(requester_user_id), 
        str(request.get_json()['reason']), 
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']), 
        str(request.get_json()['class_id']), 
        str({'scribe': 'scribe', 'relecture': 'proofread', 'edition':'edition'}[request.get_json()['timeslot_kind']])
    )
    
    if not is_slot_taken(
        str(request.get_json()['class_id']), 
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']),
        request.get_json()['timeslot_kind']
        ):

        cur = get_conn().cursor()
        cur.execute('''INSERT INTO "assigned_timeslots"
            ("user_assigned", "user_modif", "reason", "timestamp_start", "timestamp_end", "class_id", "timeslot_kind")
            VALUES (%s, %s, %s, %s, %s, %s, %s);''', data_up)
        get_conn().commit()
        # todo: add proper check commit async in front
        return jsonify({'message':"Votre choix de créneau a bien été enregistré !"})
    else:
        return jsonify({'message':"Ce créneau a été pris par un autre membre entretemps..."})

@app.route('/registerRoneoD1', methods=['POST'])
@token_required
def registerRoneoD1(user):
    requester_user_id = user['id']
    data_up = (
        str(user['id']), 
        str(requester_user_id), 
        str(request.get_json()['reason']), 
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']), 
        str(request.get_json()['class_id']), 
        str({'scribe': 'scribe', 'relecture': 'proofread', 'edition':'edition'}[request.get_json()['timeslot_kind']])
    )
    
    if not is_slot_taken(
        str(request.get_json()['class_id']), 
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']),
        request.get_json()['timeslot_kind']
        ):

        cur = get_conn().cursor()
        cur.execute('''INSERT INTO "assigned_timeslots"
            ("user_assigned", "user_modif", "reason", "timestamp_start", "timestamp_end", "class_id", "timeslot_kind")
            VALUES (%s, %s, %s, %s, %s, %s, %s);''', data_up)
        get_conn().commit()
        # todo: add proper check commit async in front
        return jsonify({'message':"Votre choix de créneau a bien été enregistré !"})
    else:
        return jsonify({'message':"Ce créneau a été pris par un autre membre entretemps..."})

@app.route('/classInfo', methods=['POST'])
@token_required
def classInfo(user):
    return jsonify(fill_blanks_in_timeslots(from_db_d1_class(request.get_json()['class_id'])))

@app.route('/isThyself', methods=['POST'])
@token_required
def isThyself(user):    
    data = request.get_json()    
    its = 'user' in data and (user['firstname'] == data['user']['firstname'] and user['lastname'] == data['user']['lastname'])
    return jsonify({'resp': its})

@app.route('/hasPlanningRights', methods=['POST'])
@token_required
def hasPlanningRights_json(user):
    return jsonify({'resp': hasPlanningRights(user)})

def hasEditionRights(user):
    db_user = get_user_by_id(user['id'])
    return db_user["right_group"] in ["presidence_P2", "planning_P2", "presidence_D1", "planning_D1", "edition_P2", "edition_D1"]

@app.route('/hasEditionRights', methods=['POST'])
@token_required
def hasEditionRights_json(user):
    return jsonify({'resp': hasEditionRights(user)})

def hasMembersManagementRights(user):
    db_user = get_user_by_id(user['id'])
    return db_user["right_group"] in ["presidence_P2", "planning_P2", "presidence_D1", "planning_D1", "edition_P2", "edition_D1", "recrutement_P2", "recrutement_D1"]

@app.route('/hasMembersManagementRights', methods=['POST'])
@token_required
def hasMembersManagementRights_json(user):
    return jsonify({'resp': hasMembersManagementRights(user)})

@app.route('/hasStarted', methods=['POST'])
@token_required_even_expired
def hasStarted(user):
    data_up = (
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']), 
        str(request.get_json()['class_id']), 
        str({'scribe': 'scribe', 'relecture': 'proofread', 'edition': 'edition'}[request.get_json()['timeslot_kind']])
    )
    
    cur = get_conn().cursor()
    cur.execute('''SELECT started_date from assigned_timeslots
            where
                timestamp_start=%s and
                timestamp_end=%s and
                class_id=%s and 
                timeslot_kind=%s
            order by id desc
            limit 1;''', data_up)
    row = cur.fetchone()
    if row is None:
        return jsonify({'resp': False})
    else:
        return jsonify({'resp': row[0] is not None})
    

@app.route('/setStarted', methods=['POST'])
@token_required_even_expired
def setStarted(user):
    data_up = (
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']), 
        str(request.get_json()['class_id']), 
        str({'scribe': 'scribe', 'relecture': 'proofread', 'edition': 'edition'}[request.get_json()['timeslot_kind']])
    )
    
    cur = get_conn().cursor()
    cur.execute('''UPDATE assigned_timeslots
                set started_date=NOW() 
                where id=(SELECT id from assigned_timeslots
                    where
                        timestamp_start=%s and
                        timestamp_end=%s and
                        class_id=%s and 
                        timeslot_kind=%s
                    order by id desc
                    limit 1)
                ;''', data_up)
    get_conn().commit()
    
    return jsonify({'message': "Vous avez indiqué avoir commencé votre partie !"})

@app.route('/hasFinished', methods=['POST'])
@token_required_even_expired
def hasFinished(user):
    data_up = (
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']), 
        str(request.get_json()['class_id']), 
        str({'scribe': 'scribe', 'relecture': 'proofread', 'edition': 'edition'}[request.get_json()['timeslot_kind']])
    )
    
    cur = get_conn().cursor()
    cur.execute('''SELECT finished_date from assigned_timeslots
            where
                timestamp_start=%s and
                timestamp_end=%s and
                class_id=%s and 
                timeslot_kind=%s
            order by id desc
            limit 1;''', data_up)
    row = cur.fetchone()
    if row is None:
        return jsonify({'resp': False})
    else:
        return jsonify({'resp': row[0] is not None})
    

@app.route('/setFinished', methods=['POST'])
@token_required_even_expired
def setFinished(user):
    data_up = (
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']), 
        str(request.get_json()['class_id']), 
        str({'scribe': 'scribe', 'relecture': 'proofread', 'edition': 'edition'}[request.get_json()['timeslot_kind']])
    )
    
    cur = get_conn().cursor()
    cur.execute('''UPDATE assigned_timeslots
                set finished_date=NOW() 
                where id=(SELECT id from assigned_timeslots
                    where
                        timestamp_start=%s and
                        timestamp_end=%s and
                        class_id=%s and 
                        timeslot_kind=%s
                    order by id desc
                    limit 1)
                ;''', data_up)
    get_conn().commit()
    
    return jsonify({'message': "Vous avez indiqué avoir fini votre partie !"})

@app.route('/cancelStarted', methods=['POST'])
@token_required_even_expired
def cancelStarted(user):
    data_up = (
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']), 
        str(request.get_json()['class_id']), 
        str({'scribe': 'scribe', 'relecture': 'proofread', 'edition': 'edition'}[request.get_json()['timeslot_kind']])
    )
    
    cur = get_conn().cursor()
    cur.execute('''UPDATE assigned_timeslots
                set started_date=null
                where id=(SELECT id from assigned_timeslots
                    where
                        timestamp_start=%s and
                        timestamp_end=%s and
                        class_id=%s and 
                        timeslot_kind=%s
                    order by id desc
                    limit 1)
                ;''', data_up)
    get_conn().commit()
    
    return jsonify({'message': "Vous avez n'avoir pas commencé votre partie !"})

@app.route('/cancelFinished', methods=['POST'])
@token_required_even_expired
def cancelFinished(user):
    data_up = (
        str(request.get_json()['timestamp_start']), 
        str(request.get_json()['timestamp_end']), 
        str(request.get_json()['class_id']), 
        str({'scribe': 'scribe', 'relecture': 'proofread', 'edition': 'edition'}[request.get_json()['timeslot_kind']])
    )
    
    cur = get_conn().cursor()
    cur.execute('''UPDATE assigned_timeslots
                set finished_date=null
                where id=(SELECT id from assigned_timeslots
                    where
                        timestamp_start=%s and
                        timestamp_end=%s and
                        class_id=%s and 
                        timeslot_kind=%s
                    order by id desc
                    limit 1)
                ;''', data_up)
    get_conn().commit()
    
    return jsonify({'message': "Vous avez indiqué n'avoir pas fini votre partie !"})

def get_verify_link(mail):
    return "http://www.apecs.ml/verify?token={}".format(
        upquote(
            jwt.encode(
                {'sub': mail, 'iat': datetime.utcnow() },
                current_app.config['SECRET_KEY'],
                algorithm="HS256"
            )
        )
    )

def verify_mail(mail):
    message = Mail(
        from_email= Email("noreply@em1318.apecs.ml", name="APECS"),
        to_emails= To(mail),
        )
    message.template_id = "d-36e0fb78659e4b74a023e29116a07d3c"
    message.dynamic_template_data = { 'verify_link': get_verify_link(mail) }
    try:
        SendGridAPIClient(os.environ.get('SENDGRID_API_KEY')).send(message)
    except Exception as e:
        logging.error(e.message)

def update_to_verified(mail):
    cur = get_conn().cursor()
    cur.execute('''UPDATE "users" SET "active_kind" = 'mail_verifie' WHERE "mail" = %s;''', (mail,))
    get_conn().commit()

@app.route('/verify', methods=('GET',))
def verifyEmail():
    token = request.args.get('token')
    try:
        decoded_mail = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])['sub']
    except Exception as e:
        logging.error(e.message)
        decoded_mail = ''
        
    update_to_verified(decoded_mail)
    return redirect("/P2/loginP2", code=302)

def is_email_verified(mail):
    cur = get_conn().cursor()
    cur.execute('''SELECT mail from users where UPPER(mail)=UPPER(%s) and ("active_kind" = 'mail_verifie' or "active_kind" = 'actif');''', (mail,))
    row = cur.fetchone()
    if row is None:
        return False
    else:
        return True

@app.route('/signup', methods=('POST',))
def registerNewUser():
    data = request.get_json()
    if get_user_by_mail(data['mail']) is not None:
        return jsonify({'message': 'Cette adresse mail est déjà utilisée.'}), 401
    cur = get_conn().cursor()
    data_up = (
        str(request.get_json()['firstname']),
        str(request.get_json()['lastname']),
        str(request.get_json()['mail']),
        str(hash_pwd(request.get_json()['mail'], request.get_json()['password'])),
        str(request.get_json()['facebook']),
        str(request.get_json()['discord']),
        str(request.get_json()['school_year']),
        "membre_D1" if "D1" in str(request.get_json()['school_year']) else "membre_P2"
    )


    if USER_REGISTERING_OPEN:
        cur.execute('''INSERT INTO "users"
            ("firstname", "lastname", "mail", "password", "facebook", "discord", "school_year", "right_group", "active_kind")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'non_verifie');''', data_up)
        get_conn().commit()
        verify_mail(str(request.get_json()['mail']))
        return jsonify({'message': 'Votre compte a bien été créé. Un mail vous a été envoyé pour confirmer votre adresse mail avant de pouvoir vous connecter.'}), 201
    else:
        cur.execute('''INSERT INTO "users"
            ("firstname", "lastname", "mail", "password", "facebook", "discord", "school_year", "right_group", "active_kind")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'attente_ok_admin');''', data_up)
        get_conn().commit()
        return jsonify({'message': 'Les inscriptions au planning ne sont pas encore ouvertes. Vous serez contacté quand vous pourrez vous inscrire.'}), 401

def authenticate(mail, password):
    cur = get_conn().cursor()
    cur.execute('''SELECT to_json(d) from (select id, firstname, lastname, mail, facebook, discord, right_group, active_kind, update_date from users where UPPER(mail)=UPPER(%s) and password=%s) as d;''', (mail, hash_pwd(mail, password)))
    row = cur.fetchone()
    if row is None:
        return None
    else:
        return row[0]

def get_user_by_mail(mail):
    cur = get_conn().cursor()
    cur.execute('''SELECT to_json(d) from (select id, firstname, lastname, mail, facebook, discord, right_group, active_kind, update_date from users where UPPER(mail)=UPPER(%s)) as d;''', (mail,))
    row = cur.fetchone()
    if row is None:
        return None
    else:
        return row[0]

def get_user_by_id(id):
    cur = get_conn().cursor()
    cur.execute('''SELECT to_json(d) from (select id, firstname, lastname, mail, facebook, discord, right_group, active_kind, update_date from users where id=%s) as d;''', (str(id),))
    row = cur.fetchone()
    if row is None:
        return None
    else:
        return row[0]

@app.route('/signin', methods=['POST'])
def logUser():
    data = request.get_json()
    user = authenticate(data['mail'].strip(), data['password'])

    if not user:
        return jsonify({ 'message': 'Identifiants incorrects. Si vous n\'arrivez pas à vous connecter, merci de le signaler sur le Discord de l\'APECS.', 'authenticated': False }), 401

    if not is_email_verified(data['mail'].strip()):
        return jsonify({ 'message': 'Vous devez confirmer votre adresse mail pour vous connecter (vous avez reçu le lien de confirmation par mail, veuillez vérifier vos dossiers spams et promotions)', 'authenticated': False }), 401

    token = jwt.encode({
        'sub': user['mail'],
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7, minutes=30)},
        current_app.config['SECRET_KEY'],
        algorithm="HS256")
    return jsonify({ 
                    'token': token, 
                    'firstname': user['firstname'],
                    'lastname': user['lastname'],
                    'hasPlanningRights': hasPlanningRights(user),
                    'hasEditionRights': hasEditionRights(user),
                    'hasMembersManagementRights': hasMembersManagementRights(user)
                    })

if __name__ == '__main__':
    pass
