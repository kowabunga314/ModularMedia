from flask import Flask, Blueprint, request
from sqlalchemy.sql import text
from app import db
from .models import User, Follow
from core.decorators import handle_exceptions
import os
import json


user = Blueprint('user', __name__)

USER_BASE_URL = '/user'

# @handle_exceptions
@user.route(USER_BASE_URL + '/<username>', methods=['GET'])
def get_user(username=None):
    if username:
        user_data = User.query.filter(User.name == username).first()
        return user_data.get()
    else:
        return 'No username provided.', 400

@user.route(USER_BASE_URL + '/create', methods=['POST'])
def create_user():
    data = request.json

    try:
        user_data = User().create(
            username=data['name'],
            email=data['email'],
            password1=data['password1'],
            password2=data['password2']
        )
    except ValueError as e:
        return e.args[0], 400

    return user_data

@user.route(USER_BASE_URL + '/update/<username>', methods=['PUT'])
def update_user(username):
    data = request.json

    # Check that username was provided and is valid
    try:
        user_data = User.query.filter(User.name == username).first()
        if user_data is None:
            raise ValueError('User not found!')
    except Exception as e:
        return 'User not found!', 400

    user_data.update(
        username=data.get('name', None),
        email=data.get('email', None),
        password1=data.get('password1', None),
        password2=data.get('password2', None),
        archived=data.get('archived', None)
    )

    return {'user_data': user_data.get()}

@user.route(USER_BASE_URL + '/delete/<username>', methods=['DELETE'])
def delete_user(username):
    users = [user for user in User().query.filter(User.name == username)]
    if len(users) < 1:
        return 'User {} not found.'.format(username), 400

    try:
        users[0].delete()
    except Exception as e:
        return e.args[0], 400

    return 'Successfully deleted {}'.format(username)


###########################################
########### User Relationships ############
###########################################

@user.route(USER_BASE_URL + '/<username>/following', methods=['GET'])
def get_following(username):
    if username:
        user = User.query.filter(User.name == username, User.archived == False).first()

        if user and user.valid():
            following = Follow().get_following(user.id)
            if following:
                return {'following': following}
            else:
                return 'User {} ({}) is not following any users.'.format(user.name, user.id), 200
        else:
            return 'User not found.', 400
    else:
        return 'No username provided.', 400

@user.route(USER_BASE_URL + '/<username>/followers', methods=['GET'])
def get_followers(username):
    if username:
        user = User.query.filter(User.name == username, User.archived == False).first()

        if user and user.valid():
            followers = Follow().get_followers(user.id)

            if followers:
                return {'followers': followers}
            else:
                return 'User {} ({}) is not followed by any users.'.format(user.name, user.id), 200
        else:
            return 'User not found.', 400

@user.route(USER_BASE_URL + '/follow', methods=['POST'])
def follow_user():
    """
        Creates relationship: originating user following target user
        Request payload: 
        {
            originating_user: username,
            target_user: username
        }
    """
    data = request.json
    originating_name = data.get('originating_user', None)
    target_name = data.get('target_user', None)

    if originating_name is None or target_name is None:
        return 'No username provided.', 400
    
    originating_user = User.query.filter(
            User.name == originating_name,
            User.archived == False
        ).first()
    target_user = User.query.filter(
            User.name == target_name,
            User.archived == False
        ).first()

    if originating_user and originating_user.valid() and target_user and target_user.valid():
        following = Follow().follow_user(originating_user.id, target_user.id, 'following')
        if following:
            return {'following': following}
        else:
            return 'Failed to create relationship.', 500
    else:
        return '{} not found.'.format('target_user' if originating_user else 'originating_user')

@user.route(USER_BASE_URL + '/unfollow', methods=['DELETE'])
def unfollow_user():
    """
        Removes relationship: originating user following target user
        Request payload: 
        {
            originating_user: username,
            target_user: username
        }
    """
    data = request.json
    originating_name = data.get('originating_user', None)
    target_name = data.get('target_user', None)

    if originating_name is None or target_name is None:
        return 'No username provided.', 400
    
    originating_user = User.query.filter(
            User.name == originating_name,
            User.archived == False
        ).first()
    target_user = User.query.filter(
            User.name == target_name,
            User.archived == False
        ).first()

    if originating_user.valid() and target_user.valid():
        relationship = Follow().unfollow_user(originating_user.id, target_user.id)
        if relationship:
            return {'status': relationship}
        else:
            return '{} is not following {}'.format(originating_user.name, target_user.name)
    else:
        return '{} not found.'.format('target_user' if originating_user else 'originating_user')


###########################################
########## Group Relationships ############
###########################################

@user.route(USER_BASE_URL + '/create', methods=['POST'])
def create_group():
    # Create group 
    # Create membership record for group creator
    pass

@user.route(USER_BASE_URL + '/update', methods=['PUT'])
def update_group_name():
    # Check for admin status
    # Change name
    # Update DB
    pass

@user.route(USER_BASE_URL + '/delete', methods=['DELETE'])
def delete_group():
    # Check for admin status
    # Delete self from DB
    pass

@user.route(USER_BASE_URL + '/join', methods=['POST'])
def join_group():
    """
        Creates relationship: user belongs to group
        Request payload: 
        {
            user: username,
            group: group ID
        }
    """
    data = request.json
    originating_name = data.get('originating_user', None)
    target_name = data.get('target_user', None)

    if originating_name is None or target_name is None:
        return 'No username provided.', 400
    
    originating_user = User.query.filter(
            User.name == originating_name,
            User.archived == False
        ).first()
    target_user = User.query.filter(
            User.name == target_name,
            User.archived == False
        ).first()

    if originating_user and originating_user.valid() and target_user and target_user.valid():
        following = Follow().follow_user(originating_user.id, target_user.id, 'following')
        if following:
            return {'following': following}
        else:
            return 'Failed to create relationship.', 500
    else:
        return '{} not found.'.format('target_user' if originating_user else 'originating_user')

def leave_group():
    # Call leave group method
    pass

def get_groups():
    # Call get all groups method
    pass

def get_group_members():
    # Call get all members method
    pass


