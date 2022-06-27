from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    fullname = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(64), nullable=False)
    team_id = db.Column(db.Integer)
    meetings = db.relationship('Meeting', backref='who_booked', lazy='dynamic')
