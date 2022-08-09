from flask_paginate import Pagination, get_page_parameter
from multiprocessing import connection
from forestoration import my_sql, bcrypt
from forestoration.authentication.routes import login_required
from forestoration.organizations.manage import *
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    g,
)
from cloudinary.uploader import upload, destroy

from forestoration.individuals.routes import individual


organization = Blueprint("organization", __name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

@organization.route('/org_dashboard/<user_email>', methods=["POST", "GET"])
@login_required
def org_dashboard(user_email):
    active = ['active']
    connection = my_sql.connect()
    curs = connection.cursor()
    curs.execute("""
        SELECT * FROM Events 
        WHERE owner = %s
        LIMIT 1""",
        (g.user[0]))
    cur= connection.cursor()
    cur.execute("""
        SELECT count(*) FROM Events
        WHERE owner = %s""",
        (g.user[0]))
    cursor = connection.cursor()
    cursor.execute("""
        SELECT count(*) FROM Events
        WHERE event_status = %s """, active)
    active = cursor.fetchall()
    count = cur.fetchall()
    event = curs.fetchall()
    return render_template("org_dashboard.html", event=event, count=count, active=active)

@organization.route("/event_org", methods=["POST", "GET"])
@login_required
def events_org():
    connection = my_sql.connect()
    curs = connection.cursor()
    curs.execute("""
        SELECT * FROM Events 
        WHERE owner = %s""",
        (g.user[0]))
    event = curs.fetchall()
    return render_template("events-org.html", event = event)

@organization.route("/insert", methods=['GET', 'POST'])
@login_required
def add_event():
    event_name = request.form['name']
    no_seed = request.form['seed']
    event_description = request.form['description']
    no_partipants = request.form['participants']
    total_cost = request.form['cost']
    venue =request.form['venue']
    variety = request.form['variety']
    start_date = request.form.get('start', False)
    rating = 0
    end_date = request.form.get('end', False)
    connection = my_sql.connect()
    cursor = connection.cursor()
    check = [event_name]

    if not event_name or not no_seed or not event_description or not no_partipants or not total_cost or not venue or not variety or not start_date or not end_date:
        flash("All fields required", "error")
        return redirect(url_for('organization.events_org'))
    else:
        if request.method == "POST":
            flash("Data Successfully Added", "success")
            connection = my_sql.connect()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT * FROM Organization
                WHERE email = %s""", (g.user[2]))
            organization = cursor.fetchone()
            cursor.execute("""
                INSERT INTO events (
                    owner, event_name, 
                    event_description, 
                    number_of_participants, 
                    number_of_seeds, venue, 
                    seedling, cost, start_date, end_date, rating) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                    (organization[0], event_name, event_description, 
                    no_partipants, no_seed, venue, 
                    variety, total_cost, start_date, end_date, rating))
            connection.commit()
            return redirect(url_for('organization.events_org')) 

@organization.route("/del_event/<string:idevent>", methods=['GET', 'POST'])
@login_required
def del_event(idevent):
    connection = my_sql.connect()   
    cursor = connection.cursor()
    cursor.execute("DELETE FROM events WHERE event_id=%s", (idevent))
    connection.commit()
    flash("Record Has Been Deleted Successfully", "success")
    return redirect(url_for('organization.events_org'))


@organization.route('/update_event',methods=['POST','GET'])
@login_required
def update_event():
    if request.method == 'POST':
        event_id = request.form['idevent']
        event_name = request.form['name']
        no_seed = request.form['seed']
        event_description = request.form['description']
        no_partipants = request.form['participants']
        total_cost = request.form['cost']
        venue = request.form['venue']
        variety = request.form['variety']
        start_date = request.form.get('start', False)
        end_date = request.form.get('end', False)
        connection = my_sql.connect()
        cursor = connection.cursor()
        cursor.execute(""" UPDATE Events SET event_name=%s, number_of_seeds=%s, event_description=%s, number_of_participants=%s, cost=%s, venue=%s, seedling=%s, start_date=%s, end_date=%s WHERE event_id=%s""", (event_name, no_seed, event_description, no_partipants, total_cost, venue, variety, start_date, end_date, event_id ) )
        flash("Record Has Been Updated Successfully", "success")
        connection.commit()
        return redirect(url_for('organization.events_org'))                


# Event Status Route
@organization.route('/event_status', defaults={'page_num': 1})
@organization.route('/event_status/<int:page>', methods=['GET'])
@login_required
def event_status(page_num):
    
    connection = my_sql.connect()
    curs = connection.cursor()

    per_page = 5
    page_num = request.args.get(get_page_parameter(), type = int, default = 1)
    offset = (page_num - 1) * per_page

    curs.execute("SELECT * FROM events")
    total = curs.fetchall()

    curs.execute("SELECT * FROM events ORDER BY start_date ASC LIMIT %s OFFSET %s", (per_page, offset))
    curs.execute("""
        SELECT * FROM Events 
        WHERE owner = %s""",
        (g.user[0]))
    total = curs.fetchall()

    curs.execute("""
        SELECT * FROM Events
        WHERE owner = %s
        ORDER BY start_date ASC 
        LIMIT %s OFFSET %s""", 
        (g.user[0], per_page, offset))
    event = curs.fetchall()

    prev_page = page_num - 1
    next_page = page_num + 1

    curs.close()

    pagination = Pagination(page = page_num, per_page = per_page, offset = offset, total = len(total), record_name = 'event')
    
    return render_template('org_event_status.html', title = "Event Status", event = event, pagination = pagination, prev_page = prev_page, next_page = next_page, page_num = page_num)


# View Participants Route
@organization.route('/view_participants', methods=['GET', "POST"])
@login_required
def view_participants():

    connection = my_sql.connect()
    cur = connection.cursor()
    cur.execute("SELECT * FROM Individual WHERE individual_id IN (SELECT individual_id FROM Participation WHERE event_id = %s)", (g.user[0],))
    participants = cur.fetchall()
    cur.close()

    return render_template("org_view_participants.html", title = "Participants", participants = participants)


# Add Participants Route
@organization.route('/add_participants/<event_id>', methods=['GET', "POST"])
@login_required
def add_participants(event_id):

    
    email = request.form['email']

    if request.method == "POST":
        connection = my_sql.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT individual_id FROM Individual
            WHERE email = %s""", (email))
        individual_id = cursor.fetchone()

        cursor.execute("""
            INSERT INTO Participation (`event_id`, `individual_id`) 
            VALUES (%s, %s)""",
            (event_id, individual_id[0]))
        connection.commit()

        flash("User added successfully.", "success")
        return redirect(url_for("organization.events_org"))


# Remove Participants Route
@organization.route("/remove_participants/<individual_id>", methods=['GET', 'POST'])
@login_required
def remove_participants(individual_id):

    connection = my_sql.connect()   
    cur = connection.cursor()
    
    cur.execute("""
        DELETE FROM Participation 
        WHERE individual_id = %s 
    """,(individual_id))
    connection.commit() 

    flash("Record Has Been Removed Successfully", "success")

    return redirect(url_for('organization.view_participants'))


@organization.route("/org_profile", methods=["POST", "GET"])
@login_required
def org_profile():
    return render_template("org_profile.html",
                            title="Organization Profile")

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@organization.route("/org_settings", methods=["POST", "GET"])
@login_required
def org_settings():
    email = g.user[2]
    file = request.files.get('file')
    new_name = request.form.get('org_name', False)
    new_email = request.form.get('org_email', False)

    email, filename = g.user[2], g.user[4]
    previous = filename.split("_")
    new = "{}_{}".format(email, int(previous[-1]) + 1)

    if file and allowed_file(file.filename):
        if request.method == "POST":
            destroy(public_id="forestoration/{}".format(filename))
            upload(file.read(), public_id="forestoration/{}".format(new))
            flash("Profile Successfully Updated", "success")

            connection = my_sql.connect()
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE Organization 
                SET full_name = %s, 
                    email = %s, 
                    filename = %s
                    WHERE email = %s""", 
                (new_name, new_email, new, email))
            connection.commit()
            return redirect(url_for('organization.org_settings'))
    else:
        if request.method == "POST":
            flash("Profile Successfully Updated", "success")
            connection = my_sql.connect()
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE organization 
                SET full_name = %s, 
                    email = %s
                    WHERE email = %s""", 
                (new_name, new_email, email))
            connection.commit()
            return redirect(url_for('organization.org_settings'))
    
    return render_template("org_profile_setting.html", title="Organization Settings", org=g.user)

@organization.route("/org_settings/password", methods=["POST", "GET"])
@login_required
def org_settings_pass():
    email = g.user[2]
    connection = my_sql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM organization WHERE email =%s", (email))
    password= cursor.fetchone()
    new_pass = request.form.get('new_pass')
    confirm_pass = request.form.get('confirm_pass')
    old_pass = request.form.get('old_pass')

    if request.method == "POST":
        if bcrypt.check_password_hash(password[0], old_pass) and new_pass == confirm_pass:
                        hashed_password = bcrypt.generate_password_hash(new_pass).decode("utf-8")
                        cursor.execute("""UPDATE organization set password=%s WHERE email=%s""", (hashed_password, email))
                        connection.commit()
                        flash("Password Successfully Updated", "success")
        elif not new_pass or not old_pass or not confirm_pass:
                    flash("All fields required", "error")
        else:
            flash("One of the credentials you've entered is incorrect. Please try again.",
                                "error")
    
                
    return render_template("org_pass_setting.html", title="Organization Settings")

@organization.route("/org_settings/notif", methods=["POST", "GET"])
@login_required
def org_settings_notif():
    return render_template("org_notif_setting.html", title="Organization Settings")

@organization.route("/org_inquiry", methods=["POST", "GET"])
@login_required
def org_inquiry():
    return render_template("inquiry_organization.html", title="Organization Inquiry")

@organization.route('/org_event_view_ratings/<event_id>', methods=['POST', 'GET'])
def event_ratings(event_id):
    rating = all_event_rating(event_id)
    rating_count = len(rating)
    connection = my_sql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Rating WHERE event_id = %s", (event_id))
    all_event_info_ratings = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('org_event_view_ratings.html', all_event_info_ratings=all_event_info_ratings, get_event_rating=get_event_rating(event_id), rating_count=rating_count, event_name=get_event_name(event_id), rater_name=get_rater_name(event_id))
