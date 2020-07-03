from flask import Flask, Blueprint, request, Response
from sqlalchemy.sql import text
from http import HTTPStatus
from app import db
from .models import User, Follow
from app.modules.group.models import Group
from .schemas import UserSchema
import os
import json


user = Blueprint('user', __name__)
user_schema = UserSchema()

USER_BASE_URL = '/user'

@user.route('', methods=['GET'])
def get_user():
    """
        get:
          summary: Get data of specific user.
          description: Returns one user if given parameters match a user in the database.
          parameters:
            - in: query
              name: uuid
              required: false
              description: The uuid of a user
            - in: query
              name: email
              required: false
              escription: The email address of a user
            - in: query
              name: name
              required: false
              description: The name of a user
            responses:
              200:
                description: Returned when a user was found
              400:
                description: Returned when no valid parameters were specified.
              404:
                description: Returned when no matching user was found.
    """
    # Get querystring args
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
        return user_schema.dump(user_data)
    else:
        return 'User not found.', 404

@user.route('/find', methods=['GET'])
def query_users():
    """
        get:
          summary: Query users.
          description: Returns a list of users based on filter criteria.
          parameters:
            - in: query
              name: username
              required: false
              description: The username of a user
            - in: query
              name: email
              required: false
              escription: The email address of a user
            - in: query
              name: name
              required: false
              description: The name of a user
            responses:
              200:
                description: Returned when a user was found
              400:
                description: Returned when no valid parameters were specified.
              404:
                description: Returned when no matching user was found.
    """
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

@user.route('/create', methods=['POST'])
def create_user():
    """
        Create a user
    """
    # Get data from request body
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

@user.route('/update', methods=['PUT'])
def update_user():
    """
        Update a user
    """
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

@user.route('/delete/<uuid>', methods=['DELETE'])
def delete_user(uuid):
    """
        Delete a user
    """
    # Query for user based on provided UUID
    if uuid:
        user_data = User.get_user(uuid=uuid)
    else:
        return 'Please provide either uuid, username, or email.', 400

    if user_data is None:
        return 'User not found.', 400

    try:
        username = user_data.username
        user_data.delete()
    except Exception as e:
        return e.args[0], 400

    return {'deleted_user': username}, 204


###########################################
########### User Relationships ############
###########################################

@user.route('/<uuid>/following', methods=['GET'])
def get_following(uuid):
    """
        Get list of other users a user is following
    """
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

@user.route('/<uuid>/followers', methods=['GET'])
def get_followers(uuid):
    """
        Get a user's followers
    """
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

@user.route('/follow', methods=['POST'])
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

@user.route('/unfollow', methods=['DELETE'])
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

@user.route('/join', methods=['POST'])
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
    """
        Remove user from a group
    """
    # Call leave group method
    pass

