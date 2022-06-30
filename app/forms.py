import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,  PasswordField, BooleanField, SubmitField, IntegerField, DateField, DateTimeField, SelectField, SelectMultipleField, widgets
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import *



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
    capacity = IntegerField('Number of Person', validators=[DataRequired()])
    remote = BooleanField('Remote', false_values=(False, 'false', 0, '0'))

    submit = SubmitField('Register')

    def validate_room(self, roomId):
        room = Room.query.filter_by(id=self.roomId.data).first()
        if room is not None:  # username exist
            raise ValidationError('Please use a different room id.')


class RoomChoice(object):
    def __iter__(self):
        rooms = Room.query.all()
        choices = [(room.id,room.roomName) for room in rooms]
        for choice in choices:
            yield choice


class UserChoice(object):
    def __iter__(self):
        users=User.query.all()
        choices=[(user.id,f'{user.fullname}, team {Team.query.filter_by(id=user.teamId).first().teamName}') for user in users]
        choices=[choice for choice in choices if 'admin' not in choice[1]]
        for choice in choices:
            yield choice



class BookmeetingForm(FlaskForm):
    title = StringField('Meeting title',validators=[DataRequired()])
    rooms = SelectField('Choose room',coerce=int,choices=RoomChoice())
    date = DateField('Choose date', format="%Y-%m-%d", validators=[DataRequired()])
    startTime = SelectField('Choose starting time(in 24hr expression)',coerce=int,choices=[(i,i) for i in range(9,21)])
    duration = SelectField('Choose duration of the meeting(in hours)',coerce=int,choices=[(i,i) for i in range(1,6)])
    #participant_users = SelectMultipleField('Choose participants',coerce=int,choices=UserChoice(),option_widget=widgets.CheckboxInput(),widget=widgets.ListWidget(prefix_label=False))
    is_confirmed = BooleanField('Confirm', false_values=(False, 'false', 0, '0'))

    submit = SubmitField('Confirm')

    '''def validate_title(self, title):
        meeting = Meeting.query.filter_by(title=self.title.data).first()
        if meeting is not None: # username exist
            raise ValidationError('Please use another meeting title.')'''

    def validate_date(self, date):
        if self.date.data < datetime.datetime.now().date():
            raise ValidationError('You can only book for day after today.')


class OccupiedRoomsForm(FlaskForm):
    date = DateField('Choose date', format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField('Check')


class DeleteUserForm(FlaskForm):
    ids = SelectField('Choose User', coerce=int, choices=UserChoice())
    submit = SubmitField('Delete')
