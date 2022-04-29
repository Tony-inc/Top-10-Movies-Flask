from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, DataRequired

class MyForm(FlaskForm):
    rating = StringField(label='Your rating')
    review = StringField(label='Your review')
    submit = SubmitField(label='Update')

class MyForm_2(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField(label='Add')