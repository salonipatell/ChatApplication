
# import required library
from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
from flask_socketio import SocketIO, emit


# import functions from db file that interact with the databse
from db import add_messages, create_user,  get_messages, get_user, get_users, block_user, is_user_blocked, unblock_user, get_blocked_users


# app initializer
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
socketio = SocketIO(app)


# all users stored with their session id
users = {}


#
@app.route('/<recipient>', methods=['GET', 'POST'])
def home(recipient):
    try:
        sender = session['username']
        recipient = recipient

        messages = get_messages(sender, recipient)
        return render_template('index.html', user=sender, recipient=recipient, messages=messages)
    except:
        return redirect(url_for('login'))


# login api that login the exist user or as a new user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        user = get_user(username)
        if user:
            session['username'] = username
        else:
            create_user(username)
            session['username'] = username

        return redirect(url_for('connect_to_user'))

    return render_template('login.html')


# api for getting all users that are connected with the logged user and a search user also...
@app.route('/users', methods=['GET', 'POST'])
def connect_to_user():
    search_user = None
    current_user = session['username']
    users = get_users(current_user)
    search_query = request.form.get('search_query', '').strip()
    blocked_users = get_blocked_users(current_user)
    if search_query:
        search_user = get_user(search_query)
    else:
        users = users
    return render_template('users.html', users=users, current_user=current_user, search_user=search_user, blocked_users=blocked_users)


# this is the socket based api that make connection for chat
@socketio.on('connect')
def get_username():
    users[session['username']] = request.sid
    print("Users:", users)


@socketio.on('private_message')
def private_message(data):
    recipient_session_id = None  # Initialize it to None
    try:
        recipient_session_id = users[data['username']]

    except:
        print("Recipient is not online!!")
    sender_session_id = request.sid

    message = data['message']
    sender = session['username']
    recipient = data['username']

    # Check if sender has blocked the recipient
    blocked_message = is_user_blocked(sender, recipient)

    if blocked_message:

        # Emit a JSON response indicating that the user is blocked
        if sender_session_id:
            emit('new_private_message', {
                 "message": f"You have blocked {recipient}"}, room=sender_session_id)
    else:
        # Add code here to block the recipient from sending a message to the sender
        sender_blocked_message = is_user_blocked(recipient, sender)

        if sender_blocked_message:

            # Emit a JSON response indicating that the sender has blocked the recipient
            if recipient_session_id:
                emit('new_private_message', {
                     "message": f"{recipient} has blocked you"}, room=sender_session_id)
        else:
            # If neither is blocked, proceed with sending the message and storing it
            add_messages(sender, recipient, message)
            new_data = {
                'message': message,
                'recipient': recipient,
                'sender': sender
            }

            if recipient_session_id:
                emit('new_private_message', new_data, room=recipient_session_id)


# this is block user api
@app.route('/block_user/<recipient>', methods=['GET', 'POST'])
def block_user_route(recipient):
    print(recipient)
    current_user = session.get('username')
    if current_user:
        block_user(current_user, recipient)
        return jsonify(f'You have blocked {recipient}.', 'success')
    return redirect(url_for('connect_to_user'))


# Route to unblock another user
@app.route('/unblock_user/<recipient>', methods=['POST'])
def unblock_user_route(recipient):
    current_user = session.get('username')
    if current_user:
        unblock_user(current_user, recipient)
        return jsonify(f'You have unblocked {recipient}.', 'success')
    return redirect(url_for('connect_to_user'))


if __name__ == '__main__':
    socketio.run(app, debug=True)
