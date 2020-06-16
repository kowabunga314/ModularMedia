from flask import Flask, Blueprint, request, Response
from sqlalchemy.sql import text
from http import HTTPStatus
from app import db
from .models import User, Follow
from core.decorators import handle_exceptions
import os
import json


user = Blueprint('user', __name__)

USER_BASE_URL = '/user'

@user.route(USER_BASE_URL, methods=['GET'])
def get_user():
    """
        get:
            summary: Get data of specific user.
            description: Returns one user if given parameters match a user in the database.
            parameters:
                uuid: The uuid of a user
                email: The email address of a user
                name: The name of a user
            responses:
                200:
                    description: Returned when a user was found
                400:
                    description: Returned when no valid parameters were specified.
                404:
                    description: Returned when no matching user was found.
    """
    # Gety querystring args
    uuid = request.args.get('uuid', None)
    email = request.args.get('email', None)
    username = request.args.get('username', None)

    # Query for user based on which args we get
    if uuid:
        user_data = User.get_user(uuid=uuid)
    elif email:
        user_data = User.get_user(email=email)
    elif username:
        user_data = User.get_user(username=username)
    else:
        return 'Please provide either uuid, username, or email.', 400

    if user_data:
        # User was found, return as dictionary
        return user_data.dict()
    else:
        return 'User not found.', 404

@user.route(USER_BASE_URL + '/find', methods=['GET'])
def query_users():
    """"""
    # Get querystring args
    params = {
        'email': request.args.get('email', None),
        'username': request.args.get('username', None),
        'name': request.args.get('name', None)
    }

    user_data = User.query_users(params)

    if user_data:
        # User was found, return as dictionary
        return {'users': [u.dict() for u in user_data]}
    else:
        return 'User not found.', 404

@user.route(USER_BASE_URL + '/create', methods=['POST'])
def create_user():
    """"""
    data = request.json

    try:
        user_data = User.create(
            name=data['name'],
            username=data['username'],
            email=data['email'],
            password1=data['password1'],
            password2=data['password2']
        )
    except ValueError as e:
        return e.args[0], 400
    except Exception as e:
        return e.args[0], 400

    return Response(json.dumps(user_data), mimetype='application/json', status=201)

@user.route(USER_BASE_URL + '/update', methods=['PUT'])
def update_user():
    """"""
    # Gety querystring args
    uuid = request.args.get('uuid', None)
    email = request.args.get('email', None)
    username = request.args.get('username', None)

    try:
        # Query for user based on which args we get
        if uuid:
            user_data = User.get_user(uuid=uuid)
        elif email:
            user_data = User.get_user(email=email)
        elif username:
            user_data = User.get_user(username=username)
        else:
            raise ValueError('User not found!')
    except Exception as e:
        return 'User not found!', 400
    # Exit if user not found
    if not user_data:
        return 'User not found!', 400

    data = request.json
    user_data.update(
        name=data.get('name', None),
        username=data.get('username', None),
        email=data.get('email', None),
        password1=data.get('password1', None),
        password2=data.get('password2', None),
        archived=data.get('archived', None)
    )

    return user_data.dict()

@user.route(USER_BASE_URL + '/delete', methods=['DELETE'])
def delete_user():
    """"""
    # Gety querystring args
    uuid = request.args.get('uuid', None)
    email = request.args.get('email', None)
    username = request.args.get('username', None)

    # Query for user based on which args we get
    if uuid:
        user_data = User.get_user(uuid=uuid)
    elif email:
        user_data = User.get_user(email=email)
    elif username:
        user_data = User.get_user(username=username)
    else:
        return 'Please provide either uuid, username, or email.', 400

    if user_data is None:
        return 'User not found.', 400

    try:
        username = user_data.username
        user_data.delete()
    except Exception as e:
        return e.args[0], 400

    return {'deleted_user': username}


###########################################
########### User Relationships ############
###########################################

@user.route(USER_BASE_URL + '/<uuid>/following', methods=['GET'])
def get_following(uuid):
    """"""
    if uuid:
        user = User.query.filter(User.uuid == uuid, User.archived == False).first()

        if user and user.valid():
            following = user.get_following()
            if following:
                return {
                    'following': following,
                    'count': len(following)
                }
            else:
                return 'User {} ({}) is not following any users.'.format(user.name, user.id), 200
        else:
            return 'User not found.', 400
    else:
        return 'No uuid provided.', 400

@user.route(USER_BASE_URL + '/<uuid>/followers', methods=['GET'])
def get_followers(uuid):
    """"""
    if uuid:
        user = User.query.filter(User.uuid == uuid, User.archived == False).first()

        if user and user.valid():
            followers = user.get_followers()

            if followers:
                return {
                    'followers': followers,
                    'count': len(followers)
                }
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
            originating_id: uuid,
            target_id: uuid
        }
    """
    data = request.json
    originating_uuid = data.get('originating_id', None)
    target_uuid = data.get('target_id', None)

    if originating_uuid is None or target_uuid is None:
        return 'No username provided.', HTTPStatus.BAD_REQUEST

    try:
        following = Follow.follow_user(originating_uuid, target_uuid, 'following')
        if following:
            return {'following': following}, HTTPStatus.CREATED
        else:
            return 'Failed to create relationship.', HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        return 'Something went wrong.', HTTPStatus.INTERNAL_SERVER_ERROR

@user.route(USER_BASE_URL + '/unfollow', methods=['DELETE'])
def unfollow_user():
    """
        Removes relationship: originating user following target user
        Request payload: 
        {
            originating_id: uuid,
            target_id: uuid
        }
    """
    data = request.json
    originating_id = data.get('originating_id', None)
    target_id = data.get('target_id', None)

    if originating_id is None or target_id is None:
        return 'No uuid provided.', 400

    try:
        relationship = Follow.unfollow_user(originating_id, target_id)
        if relationship:
            return {'status': relationship}, HTTPStatus.OK
        else:
            return 'Relationship does not exist', HTTPStatus.BAD_REQUEST
    except Exception as e:
        return e, HTTPStatus.BAD_REQUEST


###########################################
########## Group Relationships ############
###########################################

@user.route(USER_BASE_URL + '/create', methods=['POST'])
def create_group():
    """"""
    # Create group 
    # Create membership record for group creator
    pass

@user.route(USER_BASE_URL + '/update', methods=['PUT'])
def update_group_name():
    """"""
    # Check for admin status
    # Change name
    # Update DB
    pass

@user.route(USER_BASE_URL + '/delete', methods=['DELETE'])
def delete_group():
    """"""
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
    """"""
    # Call leave group method
    pass

def query_groups():
    """"""
    # Call query groups method
    pass

def get_group():
    """"""
    # Call get group method
    pass

def get_all_groups():
    """"""
    # Get all groups in database
    pass

def get_group_members():
    """"""
    # Call get all members method
    pass


