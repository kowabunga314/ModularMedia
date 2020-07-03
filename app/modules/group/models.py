from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import relationship
from app import db
from app.models import Base, MediaObject
from app.utils import generate_uuid
from app.modules.user.models import User
from datetime import datetime
import uuid
import json


class Group(MediaObject):

    def __repr__(self):
        return '<Group {}>'.format(self.name)

    @staticmethod
    def get(id=None, uuid=None, name=None):
        if id is not None:
            group = Group.query.filter(Group.id == id).first()
        elif uuid is not None:
            group = Group.query.filter(Group.uuid == uuid).first()
        elif name is not None:
            group = Group.query.filter(Group.name == name).first()
        else:
            group = None

        return group

    @staticmethod
    def create(name=None):
        group = Group(name=name)
        
        db.session.add(group)
        db.session.commit()

    def add_member(self, user_id):
        user = User.query.filter(User.id == user_id).one()

        if user:
            gm = GroupMembership(group_id=self.id, member_id=user_id)
        else:
            raise ValueError('User not found')
    
    def remove_member(self, user_id):
        gm = GroupMembership.query.filter(group_id=self.id, member_id=user_id).one()

        if gm:
            gm.delete()
        else:
            raise ValueError('User does not belong to this group')

    def get_members(self):
        relationships = GroupMembership.query.filter(GroupMembership.group_id == self.id).all()
        member_ids = [r.member_id for r in relationships]
        members = User.query.filter(User.id.in_(member_ids)).all()
        return [m for m in members]


class GroupMembership(Base):
    group_id = db.Column(db.ForeignKey('group.id'), index=True)
    member_id = db.Column(db.ForeignKey('user.id'), index=True)
    label = db.Column(db.String(32), default='belongs to')

    def __init__(self, group_id, member_id, label=None):
        self.group_id = group_id
        self.member_id = member_id
        if label is not None:
            self.label = label

    def __repr__(self):
        return '{} {} {}'.format(self.member_id, self.label, self.group_id)
    
    @staticmethod
    def get(group_id, member_id):
        relatiohship = Group.query.filter(Group.group_id == group_id, Group.member_id == member_id).first()

        if relatiohship:
            return relatiohship
        else:
            return None

