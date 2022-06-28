from flask_wtf import FlaskForm
from wtforms import StringField,  PasswordField, BooleanField, SubmitField, IntegerField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import *
import datetime


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    fullname = StringField('Full Name', validators=[DataRequired()])
    role = StringField('Role', validators=[DataRequired()], default='teacher')
    teamId = IntegerField('Team number', validators=[DataRequired()])
    teamName = StringField('Team name', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:  # username exist
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=self.email.data).first()
        if user is not None:  # username exist
            raise ValidationError('Please use a different email.')

    def validate_teamId(self, teamId):
        team = Team.query.filter_by(id=self.teamId.data).first()
        if team is not None:
            if team.teamName != self.teamName.data:
                raise ValidationError('Team name does not match, try again.')


class CreateRoomForm(FlaskForm):
    id = IntegerField('Id', validators=[DataRequired()])
    roomName = StringField('Room Name', validators=[DataRequired()])
    person_num = IntegerField('Number of Person', validators=[DataRequired()])
    remote = BooleanField('Remote', false_values=(False, 'false', 0, '0'))

    submit = SubmitField('Register')

    def validate_room(self, roomId):
        room = Room.query.filter_by(id=self.roomId.data).first()
        if room is not None:  # username exist
            raise ValidationError('Please use a different room id.')