from pymongo import MongoClient
from datetime import datetime

import pymongo

client = MongoClient('mongodb://localhost:27017')
chat_db = client.get_database('PrivateChatApp')
users_collection = chat_db.get_collection('users')
messages_collection = chat_db.get_collection('messages')


#create a new user 
def create_user(username):
    users_collection.create_index([('username', 1)], unique=True)
    return users_collection.insert_one({'username': username})


#return all user except the sender
def get_users(loggedin_user):
    recipients = messages_collection.distinct("recipient", {"sender": loggedin_user})
    senders = messages_collection.distinct("sender", {"recipient": loggedin_user})
    users_with_previous_chat = list(set(recipients).union(set(senders)))
    return users_with_previous_chat

   
#get particular user
def get_user(username):
    user = users_collection.find_one({'username': username})
    return user if user else None


#save messsages in the database
def add_messages(sender, recipient, message):
    messages_collection.insert_one({'sender': sender, 'recipient': recipient, 'message': message, 'created_at': datetime.now()})

#get message from the database
def get_messages(sender, recipient):
    messages = messages_collection.find({
        '$or': [
            {'sender': sender, 'recipient': recipient},
            {'sender': recipient, 'recipient': sender}
        ]
    }).sort('timestamp', pymongo.ASCENDING)

    message_list = []
    for message in messages:
        message_list.append({
            'sender': message['sender'],
            'recipient': message['recipient'],
            'message': message['message'],
            'created_at': message['created_at']
        })

    return message_list


# Function to block a user
def block_user(current_user, user_to_block):
    print("mamam")
    # Assuming 'current_user' is the user performing the blocking
    # Update the 'blocked_users' array for 'current_user'
    users_collection.update_one(
        {"username": current_user},
        {"$addToSet": {"blocked_users": user_to_block}}
    )


# Function to check if a user is blocked by another user
def is_user_blocked(sender_username, recipient_username):
    sender = users_collection.find_one({"username": sender_username})
    if sender and "blocked_users" in sender:
        if recipient_username in sender["blocked_users"]:
            return "User has blocked you"  # Return the specific message
    return False


# Function to unblock a user
def unblock_user(current_user, user_to_unblock):
    users_collection.update_one(
        {"username": current_user},
        {"$pull": {"blocked_users": user_to_unblock}}
    )


#get blocked user list
def get_blocked_users(username):
    blocked_users = users_collection.find({"username": username}, {"blocked_users": 1})
    
    # Extract the blocked users from the cursor
    blocked_users_list = [user for user_data in blocked_users for user in user_data.get("blocked_users", [])]

    return blocked_users_list










        
 
       