from app import flask_app

from flask import redirect, render_template, url_for, flash, request, abort
from app.forms import *
from app.models import *
from app import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


@flask_app.route('/')
def home():
    return render_template('index.html')


@flask_app.route('/about')
def about():
    return render_template('about.html')


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
        user = User(username=form.username.data, password=hashed_password, email=form.email.data,
                    fullname=form.fullname.data, role=form.role.data, teamId=form.teamId.data)
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

    return render_template('register.html', title='Register', form=form, legend='Registration Form')


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
        return redirect(url_for('account'))
    return render_template('delete_user.html', title='Delete User', form=form)


@flask_app.route('/create/room', methods=['GET', 'POST'])
@login_required
def create_room():
    form = CreateRoomForm()
    if form.validate_on_submit():
        room = Room.query.filter_by(id=form.id.data).first()
        if not room:
            new_room = Room(id=form.id.data, roomName=form.roomName.data, capacity=form.capacity.data,
                            remote=form.remote.data)
            db.session.add(new_room)
            db.session.commit()
            flash('Room created', 'success')
            return redirect(url_for('show_rooms'))
        else:
            flash('Room already existing', 'danger')
    return render_template('create_room.html', title='Create Room', form=form, legend='Create room')


@flask_app.route('/room/<int:room_id>/update', methods=['GET', 'POST'])
@login_required
def room_update(room_id):
    room = Room.query.get_or_404(room_id)
    if current_user.role != 'admin':
        flash('You need to have  admin role to update!', 'warning')
        return redirect('show_rooms')

    form = CreateRoomForm()
    if form.validate_on_submit():
        room.roomName = form.roomName.data
        room.capacity = form.capacity.data
        db.session.commit()
        flash('Room Modification successful!', 'success')
        return redirect(url_for('show_rooms'))
    form.id.data = room.id
    form.roomName.data = room.roomName
    form.capacity.data = room.capacity
    return render_template('create_room.html', title='Update Room', form=form, legend='Update room')


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
        booker = current_user

        team = Team.query.filter_by(id=current_user.teamId).first()
        room = Room.query.filter_by(id=form.rooms.data).first()
        endTime = form.startTime.data + form.duration.data
        check_capacity = room.capacity
        # Check room space availability
        all_the_meetings = db.session.query(Meeting.roomId, Meeting.startTime,
                                            db.func.sum(Meeting.students).label('sum_students')).filter_by(
            date=form.date.data).group_by(Meeting.roomId, Meeting.startTime).all()
        check_slot = Meeting.query.filter_by(date=form.date.data).filter_by(roomId=form.rooms.data).first()

        for slot_booked in all_the_meetings:
            if room.id == slot_booked[0] and form.startTime.data == slot_booked[1] and (slot_booked[2] + form.students.data) >= room.capacity:
                flash(f'Already {slot_booked[2]} students. Cannot exceed room capacity', 'warning')
                return redirect(url_for('book_meeting'))


        # check time collision
        """check_slot = Meeting.query.filter_by(date=form.date.data).filter_by(roomId=form.rooms.data).first()
        print(check_slot)
        for slot in check_slot:
            if (form.startTime.data < slot.endTime and (
                    form.startTime.data + form.duration.data) > slot.startTime):
                flash(
                    f'The time from {slot.startTime} to {slot.endTime} is already booked by {User.query.filter_by(id=slot.bookerId).first().fullname}.',
                    'warning')
                return redirect(url_for('book_meeting'))"""

        print(form.students.data, check_capacity)

        # participant_users = form.participant_users.data
        # if len(participant_users) > room.capacity:
        # flash('Max number of person reached!', 'danger')
        # return redirect(url_for('book_meeting'))

        meeting = Meeting(title=form.title.data, teamId=team.id, roomId=room.id, bookerId=booker.id,
                          date=form.date.data, startTime=form.startTime.data, endTime=endTime,
                          duration=form.duration.data, students=form.students.data, is_confirmed=form.is_confirmed.data)
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
    page = request.args.get('page', 1, type=int)
    if current_user.role == 'admin':

        meetings = Meeting.query.order_by(Meeting.date).order_by(Meeting.startTime).paginate(page=page, per_page=8)
    else:
        meetings = Meeting.query.filter_by(bookerId=current_user.id).order_by(Meeting.date).order_by(Meeting.startTime).paginate(page=page, per_page=10)
    return render_template('all_meetings.html', meetings=meetings, legend='All Meetings')


@flask_app.route('/meeting/<int:meeting_id>/update', methods=['GET', 'POST'])
@login_required
def meeting_update(meeting_id):
    meeting = Meeting.query.get_or_404(meeting_id)

    form = BookmeetingForm()
    if form.validate_on_submit():

        booker = meeting.bookerId

        team = Team.query.filter_by(id=current_user.teamId).first()
        room = Room.query.filter_by(id=form.rooms.data).first()
        endTime = form.startTime.data + form.duration.data
        check_capacity = room.capacity
        print(check_capacity, meeting.students)

        # participant_users = form.participant_users.data
        # if len(participant_users) > room.capacity:
        # flash('Max number of person reached!', 'danger')
        # return redirect(url_for('book_meeting'))
        meeting.bookerId = booker
        meeting.date = form.date.data
        meeting.startTime = form.startTime.data
        meeting.endTime = endTime
        meeting.duration = form.duration.data
        meeting.students = form.students.data
        meeting.is_confirmed = form.is_confirmed.data
        if check_capacity < meeting.students - 1:
            flash('You cannot exceed the room capacity', 'warning')
            return redirect(
                url_for('meeting_update', meeting_id=meeting.id)
            )
        db.session.commit()
        flash('Meeting Modification successful!', 'success')
        return redirect(url_for('all_meetings'))
    form.title.data = meeting.title
    form.date.data = meeting.date
    form.rooms.data=meeting.roomId
    form.startTime.data = meeting.startTime
    form.duration.data = meeting.duration
    form.students.data = meeting.students
    form.is_confirmed.data = meeting.is_confirmed
    # form.participant_users.data = meeting.participant_users

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
@login_required
def occupied_rooms():
    form = OccupiedRoomsForm()
    if form.validate_on_submit():
        rooms_occupied = []
        hours = range(9, 23)
        rooms = Room.query.all()
        all_rooms = []
        all_the_meetings = db.session.query(Meeting.roomId, Meeting.startTime, db.func.sum(Meeting.students).label('sum_students')).filter_by(date=form.date.data).group_by(Meeting.roomId, Meeting.startTime).all()
        #print(all_the_meetings)
        for my_meeting in all_the_meetings:
            print(my_meeting[1])
        for room in rooms:
            room_occupied = dict()
            room_occupied['roomId'] = room.id
            room_occupied['roomName'] = room.roomName
            #room_occupied['roomtime'] = [{'org':False,'students_num': 0, 'meetingId': 0}] * 14
            room_occupied['roomtime'] = [{'test':False, 'sum_st':0 }] * 14
            room_occupied['load'] = room.capacity

            for hour in hours:

                meetings = Meeting.query.filter_by(
                    date=form.date.data).filter_by(roomId=room.id).all()
                for my_meeting in all_the_meetings:
                    if my_meeting[1] == hour and my_meeting[0] == room.id:

                        room_occupied['roomtime'][hour - 9] = {'test': True, 'sum_st': my_meeting[2]}
                        break

                '''for meeting in meetings:
                    if meeting.endTime > (hour + 0.5) > meeting.startTime:
                        room_occupied['roomtime'][hour - 9] = {'org':True, 'students_num': meeting.students, 'meetingId': meeting.id}
                        break'''
            rooms_occupied.append(room_occupied)

            all_rooms.append({'roomName': room.roomName, 'capacity': room.capacity})
        #print(rooms_occupied)
        for room_o in rooms_occupied:
            print(room_o)
        return render_template('occupied_room_list.html', title='Rooms Occupied',
                               rooms_occupied=rooms_occupied, date=form.date.data,
                               hours=[str(hour) for hour in hours], all_rooms=all_rooms)
    return render_template('occupied_rooms.html', title='Room Occupation', form=form)

# TODO create route add student for role admin
# TODO modify available rooms route in order to count persons in room and raise Exception when capacity reached


@flask_app.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'admin':
        flash('You need to have admin role to add student!', 'warning')
        return render_template('home')
    form = CreateStudentFom()
    if form.validate_on_submit():
        student = Student.query.filter_by(id=form.id.data).first()
        if not student:
            new_student = Student(id=form.id.data, fullname=form.fullname.data, email=form.email.data,  grade=form.grade.data)
            db.session.add(new_student)
            db.session.commit()
            flash('Student created', 'success')
            return redirect(url_for('home'))
        else:
            flash('Student already existing', 'danger')
    return render_template('create_student.html', title='Create Student', form=form, legend='Create Student')


@flask_app.route('/team/create', methods=['GET', 'POST'])
@login_required
def create_team():
    if current_user.role != 'admin':
        flash('You need to have admin role to create a team', 'warning')
        return redirect(url_for('login'))

    form = CreateTeamForm()
    if form.validate_on_submit():
        team = Team(id=form.id.data, teamName=form.teamName.data)
        db.session.add(team)
        db.session.commit()
        flash(f'Team with name {team.teamName} was successfuly created', 'success')
        return redirect(url_for('create_team'))
    return render_template('create_team.html', title='Create Team', form=form, legend='Create Team')


@flask_app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('You need to have admin role to create a team', 'warning')
        return redirect(url_for('login'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, fullname=form.fullname.data, password=hashed_password, role=form.role.data, teamId=form.teamId.data)
        db.session.add(user)
        team = Team.query.filter_by(id=user.teamId).first()
        if team is None:
            newTeam = Team(id=user.teamId,
                           teamName=form.teamName.data)
            db.session.add(newTeam)
            db.session.commit()
            flash('Registered with a new team created', 'success')
            return redirect(url_for('add_user'))
        else:
            db.session.commit()
            flash('Registered to an existing team', 'success')
            return redirect(url_for('add_user'))

    return render_template('register.html', title='Add User', form=form, legend='Add User')