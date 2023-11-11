from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SearchForm(FlaskForm):
    field = SelectField('Search Field', choices=[
        ('message_id', 'Message ID'),
        ('from_email', 'From Email'),
        ('date', 'Date'),
        ('to_email', 'To Email'),
        ('subject', 'Subject'),
        ('content', 'Content')
    ])
    search = StringField('Search', validators=[DataRequired()])
    match_type = RadioField('Match Type', choices=[('exact', 'Exact'), ('partial', 'Partial')], default='partial')
    submit = SubmitField('Search')
