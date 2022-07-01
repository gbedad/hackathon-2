from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    fullname = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(64), nullable=False)
    teamId = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    #participants = db.relationship('ParticipantStudent', backref='meeting')
    meetings = db.relationship('Meeting', backref='booker', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    teamName = db.Column(db.String(64), nullable=False, unique=True)
    members = db.relationship('User', backref='team', lazy='dynamic')
    meetings = db.relationship('Meeting', backref='team', lazy='dynamic')

    def __repr__(self):
        return f'<Team {self.teamName}>'


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    roomName = db.Column(db.String(64), nullable=False)
    capacity = db.Column(db.Integer)
    remote = db.Column(db.Boolean, nullable=True)
    meetings = db.relationship('Meeting', backref='room', lazy='dynamic')

    def __repr__(self):
        return f'Room {self.roomName}'


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    fullname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    grade = db.Column(db.String(64), nullable=True)


class ParticipantStudent(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    meeting = db.Column(db.Integer, db.ForeignKey('meeting.id'))
    studentId = db.Column(db.Integer, db.ForeignKey('student.id'))


class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    title = db.Column(db.String(64), nullable=False)
    teamId = db.Column(db.Integer, db.ForeignKey('team.id'))
    roomId = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    bookerId = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.Date, nullable=False)
    startTime = db.Column(db.Integer, nullable=False)
    endTime = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    is_confirmed = db.Column(db.Boolean, nullable=True)
    students = db.Column(db.Integer, nullable=True)
    #participant_students = db.relationship('ParticipantStudent', backref='meeting')

    def __repr__(self):
        return f'Meeting {self.id} for {self.id} last for {self.duration}'


'''class Participants_user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting = db.Column(db.String(64), db.ForeignKey('meeting.title'))
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))'''


# TODO add a Student model



