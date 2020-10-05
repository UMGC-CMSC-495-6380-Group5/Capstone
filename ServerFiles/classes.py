#DATE           TEAM MEMBER         UPDATE
#//             TFEITOSA            Created classes.py
#10/03/2020     NCROWN              Updated to include revision table

from database_connector import ConnectDB
from flask_wtf import Form, FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

mydb = ConnectDB()
                                    
class NewClassForm(FlaskForm):
    class_name  = StringField('class_name', validators=[DataRequired(), Length(max=20) ] )
    date        = StringField('date')
    start_time  = StringField('start_time')
    end_time    = StringField('end_time')
    students    = StringField('students')
    instructors = StringField('instructors')
    submit      = SubmitField("Submit")