from app import flask_app

from flask import redirect, render_template, url_for, flash, request, abort
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


@flask_app.route('/delete_user', methods=['GET', 'POST'])
@login_required
def delete_user():
    if not current_user.is_authenticated:
        flash('Please Log in as admin to delete user', 'danger')
        return redirect(url_for('login'))
    if current_user.role != 'admin':
        flash('Please Log in as admin to delete user', 'danger')
        return redirect(url_for('home'))

    form = DeleteUserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.ids.data).first()

        meetings = Meeting.query.filter_by(bookerId=user.id).all()
        hasFutureBooking = False
        for meeting in meetings:
            if meeting.date > datetime.datetime.now():
                hasFutureBooking = True
                break
        if hasFutureBooking:
            flash('You cannot delete a user that holds future bookings!', 'warning')
            return redirect(url_for('delete_user'))
        elif user.id == current_user.id:
            flash('You cannot delete yourself!', 'danger')
            return redirect(url_for('delete_user'))

        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} successfully deleted! ', 'success')
        return redirect(url_for('home'))
    return render_template('delete_user.html', title='Delete User', form=form)


@flask_app.route('/create/room', methods=['GET', 'POST'])
@login_required
def create_room():
    form = CreateRoomForm()
    if form.validate_on_submit():
        room = Room.query.filter_by(id=form.id.data).first()
        if not room:
            new_room = Room(id=form.id.data, roomName=form.roomName.data, capacity=form.capacity.data, remote=form.remote.data)
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
        # check time collision
        meetingcollisions = Meeting.query.filter_by(date=datetime.datetime.combine(form.date.data,datetime.datetime.min.time())).filter_by(roomId=form.rooms.data).all()
        print(len(meetingcollisions))
        for meetingcollision in meetingcollisions:
            if (form.startTime.data < meetingcollision.endTime and (form.startTime.data+form.duration.data) > meetingcollision.startTime):
                flash(f'The time from {meetingcollision.startTime} to {meetingcollision.endTime} is already booked by {User.query.filter_by(id=meetingcollision.bookerId).first().fullname}.', 'warning')
                return redirect(url_for('book_meeting'))

        booker = current_user

        team = Team.query.filter_by(id=current_user.teamId).first()
        room = Room.query.filter_by(id=form.rooms.data).first()
        endTime = form.startTime.data + form.duration.data

        #participant_users = form.participant_users.data
        #if len(participant_users) > room.capacity:
            #flash('Max number of person reached!', 'danger')
            #return redirect(url_for('book_meeting'))

        meeting = Meeting(title=form.title.data, teamId=team.id, roomId=room.id, bookerId=booker.id,
                          date=form.date.data, startTime=form.startTime.data, endTime=endTime,
                          duration=form.duration.data, is_confirmed=form.is_confirmed.data)
        db.session.add(meeting)

        # Add participants records
        '''for participant in participant_users:
            participating = Participants_user(meeting=form.title.data, userId=participant)
            db.session.add(participating)'''

        db.session.commit()
        flash('Booking success!', 'success')
        return redirect(url_for('all_meetings'))
    return render_template('create_meeting.html', title='Book Meeting', form=form, legend='Create Meeting')


@flask_app.route('/all_meetings', methods=['GET', 'POST'])
@login_required
def all_meetings():
    if current_user.role == 'admin':
        meetings = Meeting.query.all()
    else:
        meetings = Meeting.query.filter_by(bookerId=current_user.id)
    return render_template('all_meetings.html', meetings=meetings, legend='All meetings')


@flask_app.route('/meeting/<int:meeting_id>/update', methods=['GET', 'POST'])
@login_required
def meeting_update(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)

    form = BookmeetingForm()
    if form.validate_on_submit():
        booker = current_user

        team = Team.query.filter_by(id=current_user.teamId).first()
        room = Room.query.filter_by(id=form.rooms.data).first()
        endTime = form.startTime.data + form.duration.data

        #participant_users = form.participant_users.data
        #if len(participant_users) > room.capacity:
            #flash('Max number of person reached!', 'danger')
            #return redirect(url_for('book_meeting'))
        meeting.bookerId=booker.id,
        meeting.date=form.date.data
        meeting.startTime=form.startTime.data
        meeting.endTime=endTime
        meeting.duration=form.duration.data
        meeting.is_confirmed=form.is_confirmed.data
        db.session.commit()
        flash('Meeting Modification successful!', 'success')
        return redirect(url_for('all_meetings'))
    form.title.data = meeting.title
    form.date.data = meeting.date
    form.startTime.data = meeting.startTime
    form.duration.data = meeting.duration
    form.is_confirmed.data = meeting.is_confirmed
    #form.participant_users.data = meeting.participant_users

    return render_template('create_meeting.html', title='Update Meeting', form=form, legend='Update Meeting')


@flask_app.route('/meeting/<int:meeting_id>/delete', methods=['POST'])
@login_required
def cancel_meeting(meeting_id):

    meeting = Meeting.query.get_or_404(meeting_id)
    print(meeting.title)

    if meeting.date <= datetime.datetime.now():
        flash('You cannot delete past meeting', 'warning')
        return redirect(url_for('all_meetings'))

    '''participants_user = Participants_user.query.filter_by(meeting=meeting.title).all()
    for participant in participants_user:
        print(participant)
        db.session.delete(participant)'''

    db.session.delete(meeting)
    db.session.commit()
    flash(f'Meeting "{meeting.title}" has been deleted', 'success')
    return redirect(url_for('all_meetings'))


@flask_app.route('/occupied_rooms', methods=['GET', 'POST'])
def occupied_rooms():
    form = OccupiedRoomsForm()
    if form.validate_on_submit():
        rooms_occupied = []
        hours = range(9, 23)
        rooms = Room.query.all()
        all_rooms = []
        for room in rooms:
            room_occupied = dict()
            room_occupied['roomName'] = room.roomName
            room_occupied['roomtime'] = [False]*14
            for hour in hours:
                meetings = Meeting.query.filter_by(date=datetime.datetime.combine(form.date.data,  datetime.datetime.min.time()))\
                    .filter_by(roomId=room.id).filter(Meeting.is_confirmed==True).all()

                for meeting in meetings:
                    if meeting.endTime > (hour + 0.5) > meeting.startTime:
                        room_occupied['roomtime'][hour - 9] = True
                        break
            rooms_occupied.append(room_occupied)
            all_rooms.append({'roomName': room.roomName, 'capacity': room.capacity})
        return render_template('occupied_room_list.html', title='Rooms Occupied',
                                                                    rooms_occupied=rooms_occupied, date=form.date.data,
                                   hours=[str(hour) for hour in hours], all_rooms=all_rooms)
    return render_template('occupied_rooms.html', title='Room Occupation', form=form)






