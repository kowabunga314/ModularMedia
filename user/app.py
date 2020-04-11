from flask import Flask, Blueprint, request
from app import db
from .models import User
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
            name=data['name'],
            email=data['email'],
            password1=data['password1'],
            password2=data['password2']
        )
    except ValueError as e:
        return e.args[0], 400

    return user_data

@user.route(USER_BASE_URL + '/update', methods=['PUT'])
def update_user():
    data = request.json

    # Check that username was provided and is valid
    if not data['username']:
        return 'No username provided', 400
    
    # Populate query
    query = '''
        select *
        from user
        where name=":username"
    '''

    # Set args
    args = {
        'username': data['username']
    }

    user_data = db.session.execute(query, args)

    return user_data

@user.route(USER_BASE_URL + '/archive', methods=['DELETE'])
def archive_user():
    data = request.json
    user_data = User().create(
        name=data['name'],
        email=data['email'],
        password1=data['password1'],
        password2=data['password2']
    )
    return user_data

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
