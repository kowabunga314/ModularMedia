from flask import Flask, Blueprint, request
from sqlalchemy.sql import text
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
        name=data.get('name', None),
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
