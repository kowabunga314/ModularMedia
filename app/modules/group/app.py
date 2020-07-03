from flask import Flask, Blueprint, request, Response
from sqlalchemy.sql import text
from http import HTTPStatus
from app import db
from app.modules.user.models import User, Follow
from .schemas import GroupSchema
import os
import json


group = Blueprint('group', __name__)
group_schema = GroupSchema()



###########################################
########## Group Relationships ############
###########################################

@group.route('/create', methods=['POST'])
def create_group():
    """
        Create a group
    """
    # Create group 
    # Create membership record for group creator
    pass

@group.route('/update', methods=['PUT'])
def update_group_name():
    """
        Update the name of a group
    """
    # Check for admin status
    # Change name
    # Update DB
    pass

@group.route('/delete', methods=['DELETE'])
def delete_group():
    """
        Delete a group
    """
    # Check for admin status
    # Delete self from DB
    pass

@group.route('/join', methods=['POST'])
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

def query_groups():
    """
        Find groups based on filter criteria
    """
    # Call query groups method
    pass

def get_group():
    """
        Get a group
    """
    # Call get group method
    pass

def get_all_groups():
    """
        Get all groups...why?
    """
    # Get all groups in database
    pass

def get_group_members():
    """
        Get all members of a group
    """
    # Call get all members method
    pass


