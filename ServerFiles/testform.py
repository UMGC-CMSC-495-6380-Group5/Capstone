from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class TestForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), 
                                                Length(min=2, max=20)])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), EqualTo('password')])
    confirm_password = PasswordField("Confirm Password")
    submit = SubmitField("Submit Data")