from flask_wtf import FlaskForm
from forestoration import my_sql
from flask_wtf.file import (
    FileAllowed,
    FileField
)
from wtforms import (
    PasswordField,
    StringField, 
    SubmitField, 
    SelectField,
)
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length, 
    Email,
    ValidationError
)

class RegistrationForm(FlaskForm):
    organization_or_full_name = StringField("Organization Name or Full Name",
                                    render_kw={"placeholder": "Save Forests or Joshua"},
                                    validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Your Email Address",
                        render_kw={"placeholder": "forestoration@example.com"}, 
                        validators=[DataRequired(), 
                        Email(message="Invalid email address.")])
    password = PasswordField("Password", 
                            validators=[DataRequired(), 
                            EqualTo("confirm_password", 
                            message="Passwords should match.")])
    confirm_password = PasswordField("Confirm Password")
    user_type = SelectField("User Type", 
                            choices=["Individual", "Organization"])
    profile_picture = FileField("Upload Profile",
                                validators=[FileAllowed(["png", "jpg", "jpeg"])])
    sign_up = SubmitField("Sign Up")

    def validate_email(self, email):
        connection = my_sql.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM Individual 
            WHERE email = %s""", 
            (email.data,))
        individual_email = cursor.fetchone()
        
        cursor.execute("""
            SELECT * FROM Organization 
            WHERE email = %s""", 
            (email.data,))
        organization_email = cursor.fetchone()

        if individual_email or organization_email:
            raise ValidationError("This email is already taken.")

class LoginForm(FlaskForm):
    email = StringField("Your Email Address",
                        render_kw={"placeholder": "forestoration@example.com"}, 
                        validators=[DataRequired(), Email(message="Invalid email address.")])
    password = PasswordField("Password", 
                            validators=[DataRequired()])
    user_type = SelectField("User Type", 
                            choices=["Individual", "Organization"])
    login = SubmitField("Log In")
    
    