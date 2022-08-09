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

def all_event_rating(event_id):
    connection = my_sql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT rating_rating FROM Rating WHERE event_id = %s", (event_id))
    all_event_rating = cursor.fetchall()
    cursor.close()
    connection.close()
    return tuple(itertools.chain(*all_event_rating))

def get_event_rating(event_id):
    connection = my_sql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT rating FROM Events WHERE event_id = %s", (event_id))
    rating = cursor.fetchone()
    get_event_rating = functools.reduce(lambda sub, elem: sub * 10 + elem, rating)
    cursor.close()
    connection.close()
    return get_event_rating

def get_event_name(event_id):
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT event_name FROM Events WHERE event_id = %s", event_id)
    get_event_name = cursor.fetchone()
    cursor.close()
    connection.close()
    return get_event_name["event_name"]

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
