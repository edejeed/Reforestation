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
    RadioField,
)
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length, 
    Email,
    ValidationError
)

class RatingForm(FlaskForm):
    review = StringField(
        label = ("Write your review here."),
        validators = [DataRequired()],
        render_kw={'type': 'text'}
    )

    rating = RadioField(
        label = ('How do you rate the event?'),
        validators=[DataRequired()],
        choices=[
            (5,'5 (Best)'),
            (4,'4 (Good)'),
            (3,'3 (Average)'),
            (2,'2 (Poor)'),
            (1,'1 (Worst)'),
        ]
    )
    
    submit = SubmitField(
        label=('Submit Rating'),
        render_kw={'class': 'btn btn-outline-secondary btn-block'}
    )