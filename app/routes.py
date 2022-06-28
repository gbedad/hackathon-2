from app import flask_app

from flask import redirect, render_template, url_for, flash, request
from app.forms import *
from app.models import *
from app import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


@flask_app.route('/')
def home():
    return render_template('index.html')


@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('account'))
        else:
            flash('Login Unsuccessful, please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@flask_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password,email=form.email.data, fullname=form.fullname.data, role=form.role.data,teamId=form.teamId.data)
        db.session.add(user)
        team = Team.query.filter_by(id=user.teamId).first()
        if team is None:
            newTeam = Team(id=user.teamId,
                           teamName=form.teamName.data)
            db.session.add(newTeam)
            db.session.commit()
            flash('Registered with a new team created', 'success')
            return redirect(url_for('login'))
        else:
            db.session.commit()
            flash('Registered to an existing team', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@flask_app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@flask_app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')
