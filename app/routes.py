from app import flask_app

from flask import redirect, render_template, url_for, flash
from app.forms import *
from app.models import *
from app import db


@flask_app.route('/')
def index():
    return render_template('index.html')


@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
    return render_template('login.html', form=form)


@flask_app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.validate_on_submit():
            user = User(username=form.username.data,
                        fullname=form.fullname.data,
                        role=form.position.data,
                        teamId=form.teamId.data)
            user.set_password(form.password.data)
            db.session.add(user)
            team = Team.query.filter_by(id=user.teamId).first()
            if team is None:
                newTeam = Team(id=user.teamId,
                               teamName=form.teamName.data)
                db.session.add(newTeam)
                db.session.commit()
                flash('Registered with a new team created')
                return redirect(url_for('login'))
            else:
                db.session.commit()
                flash('Registered to an existing team')
                return redirect(url_for('login'))

    return render_template('register.html', form=form)
