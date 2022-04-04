from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User


class RegistrationForm(FlaskForm):
   username = StringField('Username', validators=[DataRequired(), Length(min=2, max= 20)])
   email= StringField('Email', validators=[DataRequired(), Email()])
   password= PasswordField('Password', validators=[DataRequired()])
   confirm_password= PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
   about_me=TextAreaField('About Me', validators=[DataRequired()])
   level=SelectField('Level',choices=['Beginner', 'Intermediate', 'Expert'], validators=[DataRequired()])
   area=StringField('Area', validators=[DataRequired()])
   lookup_address = StringField('Search address') ##
   coord_latitude = HiddenField('Latitude',validators=[DataRequired()])##
   coord_longitude = HiddenField('Longitude', validators=[DataRequired()])##
   submit= SubmitField('Sign Up')

   def validate_username(self, username):
        user= User.query.filter_by(username=username.data).first() 
        if user:
           raise ValidationError('That username already exists')

   def validate_email(self, email):
        user= User.query.filter_by(email=email.data).first() 
        if user:
           raise ValidationError('That email already exists')



class LoginForm(FlaskForm):
   email= StringField('Email', validators=[DataRequired(), Email()])
   password= PasswordField('Password', validators=[DataRequired()])
   remember= BooleanField('Remember Me')
   submit= SubmitField('Log In')


class UpdateSettingsForm(FlaskForm):
     username = StringField('Username', validators=[DataRequired(), Length(min= 2, max = 20)])

     email = StringField('Email', validators=[DataRequired(), Email()])
     password= PasswordField('Password', validators=[DataRequired()])
     picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
     
     about_me=TextAreaField('About Me', validators=[DataRequired()])
     level=SelectField('Level',choices=['Beginner', 'Intermediate', 'Expert'], validators=[DataRequired()])
     area=StringField('Area', validators=[DataRequired()])
     lookup_address = StringField('Search address') ##
     coord_latitude = HiddenField('Latitude',validators=[DataRequired()])##
     coord_longitude = HiddenField('Longitude', validators=[DataRequired()])##
     submit = SubmitField('Update')
    
     def validate_username(self, username):
          if username.data != current_user.username:
              user= User.query.filter_by(username = username.data).first()
          
              if user:
                raise ValidationError('That username already exists.')

     def validate_email(self, email):
          if email.data != current_user.email:
             user= User.query.filter_by(email = email.data).first()
          
             if user:
                raise ValidationError('That Email already exists.')

class NewLocationForm(FlaskForm):
   description = StringField('Location description', validators=[DataRequired(), Length(min=1, max=80)])

   lookup_address = StringField('Search address')
   coord_latitude = HiddenField('Latitude',validators=[DataRequired()])
   coord_longitude = HiddenField('Longitude', validators=[DataRequired()])
   submit = SubmitField('Create Location')