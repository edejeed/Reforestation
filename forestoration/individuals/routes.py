import pymysql
from datetime import datetime
from cloudinary.uploader import upload, destroy
from forestoration.authentication.routes import login_required
from forestoration import my_sql
from forestoration.individuals.forms import *
from forestoration.individuals.manage import *
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

from forestoration.individuals.manage import rating_exists

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

individuals = Blueprint("individual", __name__)

@individuals.route("/individual/<user_email>", methods=["POST", "GET"])
@login_required
def individual(user_email):
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT * FROM Events 
        WHERE event_id NOT IN 
        (SELECT event_id FROM Participation 
        WHERE individual_id = %s)""",
        g.user[0])
    events = cursor.fetchall()

    return render_template("events.html",
                            title="User Dashboard",
                            events=events)

@individuals.route("/joined/<user_email>", methods=["POST", "GET"])
@login_required
def joined(user_email):
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT * FROM Events 
        WHERE event_id IN 
        (SELECT event_id FROM Participation 
        WHERE individual_id = %s)""",
        g.user[0])
    events = cursor.fetchall()

    return render_template("joined.html",
                            title="User Dashboard",
                            events=events)

@individuals.route("/individual_profile", methods=["POST", "GET"])
@login_required
def individual_profile():
    return render_template("individual_profile.html",
                            title="Individual Profile")

@individuals.route("/join", methods=["POST", "GET"])
@login_required
def join():
    if request.method == "POST":
        connection = my_sql.connect()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Participation (`event_id`, `individual_id`) 
            VALUES (%s, %s)""",
            (request.form["event_id"], g.user[0]))
        connection.commit()

        flash("We are grateful for your participatory act.", "success")
        return redirect(url_for("individual.individual", user_email=g.user[2]))

@individuals.route("/organization", methods=["POST", "GET"])
@login_required
def organization():
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Organization")
    organization = cursor.fetchall()
    
    return render_template("individual_organization.html",
                        organization=organization)

@individuals.route("/inquiry", methods=["POST", "GET"])
@login_required
def inquiry():
    return render_template("inquiry_individual.html",
                            title="Inquiry")

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@individuals.route("/individual_setting", methods=["POST", "GET"])
@login_required
def individuals_settings():
    email = g.user[2]
    file = request.files.get('file')
    new_name = request.form.get('user_name', False)
    new_email = request.form.get('user_email', False)
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
                UPDATE Individual 
                SET full_name = %s, 
                    email = %s, 
                    filename = %s
                    WHERE email = %s""", 
                (new_name, new_email, new, email))
            connection.commit()
    else:
        if request.method == "POST":
            flash("Profile Successfully Updated", "success")
            connection = my_sql.connect()
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE Individual 
                SET full_name = %s, 
                    email = %s
                    WHERE email = %s""", 
                (new_name, new_email, email))
            connection.commit()
    return render_template("individual_profile_setting.html", title="Individual Settings", user=g.user)

@individuals.route("/individual_pass_setting", methods=["POST", "GET"])
@login_required
def individuals_pass_settings():
    email = g.user[2]
    connection = my_sql.connect()
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM individual WHERE email =%s", (email))
    password= cursor.fetchone()
    new_pass = request.form.get('new_pass')
    confirm_pass = request.form.get('confirm_pass')
    old_pass = request.form.get('old_pass')

    if request.method == "POST":
        if bcrypt.check_password_hash(password[0], old_pass) and new_pass == confirm_pass:
                        hashed_password = bcrypt.generate_password_hash(new_pass).decode("utf-8")
                        cursor.execute("""UPDATE individual set password=%s WHERE email=%s""", (hashed_password, email))
                        connection.commit()
                        flash("Password Successfully Updated", "success")
        elif not new_pass or not old_pass or not confirm_pass:
                    flash("All fields required", "danger")
        else:
            flash("One of the credentials you've entered is incorrect. Please try again.",
                                "error")
    return render_template("individual_pass_setting.html", title="Individual Settings")

@individuals.route("/individual_notif_setting", methods=["POST", "GET"])
@login_required
def individuals_notif_settings():
    return render_template("individual_notif_setting.html", title="Individual Settings")

@individuals.route('/rate/<event_id>', methods=['POST', 'GET'])
def rate(event_id):
    individual = g.user[0]

    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    if rating_exists(individual, event_id):
        return redirect(f"/edit-rating/{event_id}")
    
    form = RatingForm()
    if form.validate_on_submit():
        query = """
                INSERT INTO `Rating` (
                    `individual_id`,
                    `event_id`,
                    `rating_review`,
                    `rating_rating`,
                    `rating_date`
                    )
                VALUES (%s, %s, %s, %s, %s)
                """
        data = (                    
                individual,
                event_id,
                form.review.data,
                form.rating.data,
                datetime.now().strftime('%Y-%m-%d')
                )
        cursor.execute(query, data)
        cursor.close()
        connection.commit()
        connection.close()
        update_rating(event_id)
        flash('The event is rated successfully', 'success')
        return redirect('/i-rated')
    else:
        return render_template('rating_individual.html', form=form, event_name=get_event_name(event_id))

@individuals.route('/edit-rating/<event_id>', methods=['POST', 'GET'])
def edit_rating(event_id):
    individual = g.user[0]
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT rating_review AS review,
                rating_rating AS rating,
                individual_id,
                event_id
        FROM Rating
        WHERE individual_id = %s AND event_id = %s""", (individual, event_id))
        
    rating_info = cursor.fetchone()
    cursor.close()
    connection.commit()
    connection.close()

    if individual != rating_info['individual_id']:
        message = flash("No rating found", "warning")
        return message
    else:
        form = RatingForm(data=rating_info)
            
        if form.validate_on_submit():
            query = """
                UPDATE Rating 
                SET rating_review = %s,
                    rating_rating = %s,
                    rating_date = %s
                WHERE individual_id = %s AND event_id = %s
                """

            data = (form.review.data,
                    form.rating.data,
                    datetime.now().strftime('%Y-%m-%d'),                
                    individual,
                    event_id,
                )
            connection = my_sql.connect()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, data)
            cursor.close()
            connection.commit()
            connection.close()

            update_rating(event_id)
            flash('The rating is updated successfully', 'success')
            return redirect('/i-rated')
        else:
            return render_template("individual_edit_rating.html", form=form, event_name=get_event_name(event_id))

@individuals.route('/i-rated', methods=['POST', 'GET'])
def i_rated():
    individual = g.user[0]
    i_rated = all_events_i_rated(individual)
    return render_template("individual_rating_page.html", i_rated=i_rated)

@individuals.route('/delete-rating/<event_id>', methods=['POST', 'GET'])
def delete_rating(event_id):
    individual = g.user[0]
    connection = my_sql.connect()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT rating_review,
                    rating_rating,
                    rating_date,
                    individual_id,
                    event_id
        FROM Rating
        WHERE individual_id = %s AND event_id = %s""", (individual, event_id))
    rating_info = cursor.fetchone()
    cursor.close()
    connection.commit()
    connection.close()

    if individual != rating_info['individual_id']:
        message = flash("No rating found", "warning")
        return message
    else:
        connection = my_sql.connect()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            DELETE FROM Rating
            WHERE individual_id = %s AND event_id = %s""", (individual, event_id))
        cursor.close()
        connection.commit()
        connection.close()

        update_rating(event_id)
        flash('The rating is deleted successfully', 'success')
        return redirect('/i-rated')

@individuals.route('/view_event_ratings/<event_id>', methods=['POST', 'GET'])
def event_rates(event_id):
    rating = all_event_rating(event_id)
    rating_count = len(rating)

    return render_template('individual_view_event_rating.html', event_rating=event_rating(event_id), get_event_rating=get_event_rating(event_id), rating_count=rating_count, event_name=get_event_name(event_id), rater_name=get_rater_name(event_id))
