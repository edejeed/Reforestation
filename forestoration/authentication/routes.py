import functools
from cloudinary.uploader import upload
from forestoration import my_sql, bcrypt
from forestoration.authentication.forms import LoginForm, RegistrationForm
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    g
)

authentication = Blueprint("authentication", __name__)

@authentication.before_app_request
def load_logged_in_user():
    user_email = session.get("user_email")
    connection = my_sql.connect()   
    cursor = connection.cursor()

    if user_email is None:
        g.user = None
    else:
        cursor.execute("""
            SELECT * FROM Individual 
            WHERE email = %s""",  
            (user_email,))
        g.user = cursor.fetchone()
        if not g.user:
            cursor.execute("""
                SELECT * FROM Organization 
                WHERE email = %s""",  
                (user_email,)) 
            g.user = cursor.fetchone()

@authentication.route("/logout")
def logout():
    session.clear()       
    return redirect(url_for("authentication.index"))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("authentication.index"))
        
        return view(**kwargs)
    return wrapped_view

@authentication.route("/", methods=["POST", "GET"])
def index():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        connection = my_sql.connect()
        cursor = connection.cursor()

        email = form.email.data
        password = form.password.data
        user_type = form.user_type.data

        if user_type == "Individual":
            cursor.execute("""
                SELECT * FROM Individual 
                WHERE email = %s""", 
                (email,))
            individual = cursor.fetchone()
        
            if individual and bcrypt.check_password_hash(individual[3], password):
                session["user_email"] = email
                return redirect(url_for("individual.individual", 
                                        user_email=individual[2]))
            else:
                flash("One of the credentials you've entered is incorrect. \
                    Please try again.", "danger")
        else:
            cursor.execute("""
                SELECT * FROM Organization 
                WHERE email = %s""", 
                (email,))
            organization = cursor.fetchone()
        
            if organization and bcrypt.check_password_hash(organization[3], password):
                session["user_email"] = email
                return redirect(url_for("organization.org_dashboard", 
                                        user_email=organization[2]))
            else:
                flash("One of the credentials you've entered is incorrect. \
                    Please try again.", "danger")

    return render_template("index.html", 
                            title="Forest Restoration",
                            form=form)

@authentication.route("/register", methods=["POST", "GET"])                                                      
def register():
    form = RegistrationForm()

    if request.method == "POST" and form.validate_on_submit():
        connection = my_sql.connect()
        cursor = connection.cursor()

        email = form.email.data
        user_type = form.user_type.data
        filename = "{}_1".format(email)
        profile_picture = form.profile_picture.data
        organization_or_full_name = form.organization_or_full_name.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        if profile_picture:
            upload(profile_picture.read(), 
            public_id="forestoration/{}".format(filename))

        if user_type == "Individual":
            cursor.execute("""
                INSERT INTO Individual (`full_name`, `email`, `password`, `filename` ) 
                VALUES (%s, %s, %s, %s)""", 
                (organization_or_full_name, email, hashed_password, filename))
        else:
            cursor.execute("""
                INSERT INTO Organization (`full_name`, `email`, `password`, `filename`) 
                VALUES (%s, %s, %s, %s)""", 
                (organization_or_full_name, email, hashed_password, filename))

        connection.commit()

        flash("Your account has been created successfully.", "success")
        return redirect(url_for("authentication.index"))

    return render_template("register.html",
                            title="Register",
                            form=form)