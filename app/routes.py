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


@flask_app.route('/create/room', methods=['GET', 'POST'])
@login_required
def create_room():
    form = CreateRoomForm()
    if form.validate_on_submit():
        room = Room.query.filter_by(id=form.id.data).first()
        if not room:
            new_room = Room(id=form.id.data, roomName=form.roomName.data, person_num=form.person_num.data, remote=form.remote.data)
            db.session.add(new_room)
            db.session.commit()
            flash('Room created', 'success')
            return redirect(url_for('show_rooms'))
        else:
            flash('Room already existing', 'danger')
    return render_template('create_room.html', title='Create Room', form=form)


@flask_app.route('/show_rooms', methods=['GET'])
@login_required
def show_rooms():
    rooms = Room.query.all()
    return render_template('show_rooms.html', rooms=rooms)


@flask_app.route('/book', methods=['GET', 'POST'])
@login_required
def book_meeting():
    form = BookmeetingForm()
    if form.validate_on_submit():



        # make booking
        booker = current_user

        team = Team.query.filter_by(id=current_user.teamId).first()
        room = Room.query.filter_by(id=form.rooms.data).first()
        endTime = form.startTime.data + form.duration.data

        participants_user = form.participants_user.data
        if len(participants_user) > room.person_num:
            flash('Max number of person reached!', 'danger')
            return redirect(url_for('book_meeting'))

        meeting = Meeting(title=form.title.data, teamId=team.id, roomId=room.id, bookerId=booker.id,
                          date=form.date.data, startTime=form.startTime.data, endTime=endTime,
                          duration=form.duration.data)
        db.session.add(meeting)

        db.session.commit()
        flash('Booking success!', 'success')
        return redirect(url_for('all_meetings'))
    return render_template('book_room.html', title='Book Meeting', form=form)


@flask_app.route('/all_meetings', methods=['GET', 'POST'])
@login_required
def all_meetings():
    if current_user.role == 'admin':
        meetings = Meeting.query.all()
    else:
        meetings = Meeting.query.filter_by(bookerId=current_user.id)
    return render_template('all_meetings.html', meetings=meetings)