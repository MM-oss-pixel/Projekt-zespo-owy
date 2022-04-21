from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators = [DataRequired(),  Length(min=8, max=32)])
    confirmPassword = PasswordField('Password', validators = [DataRequired(), Length(min=8, max=32), EqualTo('password')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    sex = SelectField('sex', choices=[("K", "Kobieta"), ("M","Męzczyzna")])
    age = IntegerField('age', validators=[DataRequired()])
    confirmEmail = StringField('confirmEmail', validators=[DataRequired(), Email(), EqualTo('email')])
    termsAccepted = BooleanField('Accepted')
    submit = SubmitField('Rejestracja')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired(),  Length(min=8, max=32)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Zaloguj')