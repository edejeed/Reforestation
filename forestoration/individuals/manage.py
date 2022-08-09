import pymysql, itertools
import functools
from flask import session
from forestoration import my_sql, bcrypt
from flask import (
    Blueprint,
    g,
    flash,
    request,
    session,
    url_for,
    redirect,
    render_template
)

def rating_exists(individual_id, event_id):
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    query = """
            SELECT `rating_review`,
                `rating_rating`,
                `rating_date`
            FROM `Rating`
            WHERE `individual_id` = %s AND `event_id` = %s
            """ 
    data = (                    
            individual_id,
            event_id
        )
    cursor.execute(query, data)
    rating = cursor.fetchone()
    cursor.close()
    connection.commit()
    connection.close()
    return bool(rating)

def all_event_rating(event_id):
    connection = my_sql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT rating_rating FROM Rating WHERE event_id = %s", (event_id))
    all_event_rating = cursor.fetchall()
    cursor.close()
    connection.close()
    return tuple(itertools.chain(*all_event_rating))

def get_rating(event_id):
    connection = my_sql.connect()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT rating_review,
            rating_rating
        FROM Rating
        WHERE event_id = %s""", (event_id))
    get_rating = cursor.fetchall()
    cursor.close()
    connection.close()
    return get_rating

def update_rating(event_id):
    rating = all_event_rating(event_id)
    rating_count = len(rating)
    if rating_count == 0:
        connection = my_sql.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("UPDATE Events SET rating = %s WHERE `event_id` = %s", (0, event_id))
        cursor.close()
        connection.commit()
        connection.close()
    else:
        average_rating = sum(rating) / rating_count
        connection = my_sql.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("UPDATE Events SET rating = %s WHERE event_id = %s", (average_rating, event_id))
        cursor.close()
        connection.commit()
        connection.close()

def get_event_name(event_id):
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT event_name FROM Events WHERE event_id = %s", event_id)
    get_event_name = cursor.fetchone()
    cursor.close()
    connection.close()
    return get_event_name["event_name"]

def all_events():
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT * FROM Events 
        WHERE event_id IN 
        (SELECT event_id FROM Participation 
        WHERE individual_id = %s)""",
        g.user[0])
    events = cursor.fetchall()
    cursor.close()
    connection.close()
    return events

def all_events_i_rated(individual_id):
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT Rating.rating_id,
            Rating.individual_id,
            Rating.event_id,
            Rating.rating_review,
            Rating.rating_rating,
            Rating.rating_date,
            Events.event_name As rating_event_name
        FROM Rating
        JOIN Events ON Events.event_id = Rating.event_id
        WHERE individual_id = %s""", (individual_id))
    all_events_i_rated = cursor.fetchall()
    cursor.close()
    connection.close()
    return all_events_i_rated

def get_event_rating(event_id):
    connection = my_sql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT rating FROM Events WHERE event_id = %s", (event_id))
    rating = cursor.fetchone()
    get_event_rating = functools.reduce(lambda sub, elem: sub * 10 + elem, rating)
    cursor.close()
    connection.close()
    return get_event_rating

def get_rater_name(event_id):
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT Rating.rating_id,
            Rating.individual_id,
            Individual.full_name As rater_name
        FROM Rating
        JOIN Individual ON Individual.individual_id = Rating.individual_id
        WHERE event_id = %s""", (event_id))
    get_rater_name = cursor.fetchone()
    cursor.close()
    connection.close()
    return get_rater_name["rater_name"]

def event_rating(event_id):
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Rating WHERE event_id = %s", event_id)
    event_rating = cursor.fetchall()
    cursor.close()
    connection.close()
    return event_rating