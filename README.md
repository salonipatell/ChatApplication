# ChatApplication
This is a simple chat application built using Flask and Flask-SocketIO. It allows users to log in, connect with other users, send private messages, block/unblock users, and view their message history.

## Routes

### Home
- **Route**: `/recipient`
- **Description**: Displays the chat interface between the logged-in user and a recipient. Users can send and receive messages here.

### Login
- **Route**: `/login`
- **Description**: Allows users to log in using their username. If the username doesn't exist, it will be created.

### User List
- **Route**: `/users`
- **Description**: Displays a list of users that already connected with the sender in past. Users can click on a username to initiate a chat or user can also search by their username.

### Block User
- **Route**: `/block_user/<recipient>`
- **Description**: Allows a user to block another user. The blocked user won't be able to send messages to the user who blocked them.

### Unblock User
- **Route**: `/unblock_user/<recipient>`
- **Description**: Allows a user to unblock a previously blocked user. This restores the ability for the unblocked user to send messages.

## Usage

1. Start the application by running `python app.py` in your terminal.
2. Open your web browser and navigate to `http://localhost:5000/login`.
