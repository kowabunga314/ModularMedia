from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import relationship
from app import db
from app.models import Base, MediaObject
from app.utils import generate_uuid
from datetime import datetime
import uuid
import json

class User(UserMixin, MediaObject):
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))

    def __init__(self, username, email, password, name=None):
        self.username = username
        self.email = email
        self.password = password
        super().__init__(name=name)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def _to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'archived': self.archived
        }

    def dict(self):
        if self.archived:
            return self._get_archived()
        else:
            return self._to_dict()

    @staticmethod
    def get_user(id=None, uuid=None, username=None, email=None):
        if id is not None:
            user = User.query.filter(User.id == id).first()
        elif uuid is not None:
            user = User.query.filter(User.uuid == uuid).first()
        elif username is not None:
            user = User.query.filter(User.username == username).first()
        elif email is not None:
            user = User.query.filter(User.email == email).first()
        else:
            user = None

        return user
    
    @staticmethod
    def create(name, username, email, password1, password2):
        # Verify that passwords match
        if password1 != password2:
            msg = 'passwords do not match.'
            raise ValueError(msg)

        # Verify that name is unique
        if User.query.filter(User.username == username).count():
            raise ValueError('That username is already taken!')

        # Verify that email is unique
        if User.query.filter(User.email == email).count():
            raise ValueError('An account with that email already exists!')

        # Create the user
        user = User(
            name=name,
            username=username,
            email=email,
            password=generate_password_hash(password1)
        )
        db.session.add(user)
        db.session.commit()
        return user.dict()

    def update(self, name=None, username=None, email=None, password1=None, password2=None, archived=None):
        self.name = name or self.name
        self.username = username or self.username
        self.email = email or self.email

        # Handle password change
        if password1 and password1 == password2:
            self.password = generate_password_hash(password1)

        self.archived = archived if archived is not None else self.archived

        db.session.commit()
        return self.dict()

    def get_followers(self):
        return [f.originating_user.dict() for f in self.followers]

    def get_following(self):
        return [f.target_user.dict() for f in self.following]
    
    def is_following(self, target_user_id):
        relationship = Follow.get(self.uuid, target_user_id)

        return True if relationship else False
    
    def belongs_to_group(self, group_id):
        relationship = GroupMembership.query.filter(GroupMembership.member_id == self.id, GroupMembership.group_id == group_id)

        return True if relationship.one() else False


class Follow(Base):
    originating_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    target_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    label = db.Column(db.String)

    def __repr__(self):
        return '{} {} {}'.format(self.originating_id, self.label, self.target_id)
    
    @staticmethod
    def get(ou_id, tu_id):
        relatiohship = Follow.query.filter(Follow.originating_id == ou_id, Follow.target_id == tu_id).first()

        if relatiohship:
            return relatiohship
        else:
            return None

    def follow_user(self, ou, tu, label='following'):
        # Get users referenced in params
        originating_user = User.query.filter(
                User.uuid == ou,
                User.archived == False
            ).first()
        target_user = User.query.filter(
                User.uuid == tu,
                User.archived == False
            ).first()

        # Validate both users exist, are valid, and relationship does not already exist
        if originating_user and originating_user.valid() and target_user and target_user.valid() and not originating_user.is_following(target_user.uuid):
            self.originating_id = ou
            self.target_id = tu
            self.label = label

            db.session.add(self)
            db.session.commit()
            return self.__repr__()

    @staticmethod
    def unfollow_user(ou, tu):
    
        originating_user = User.query.filter(
                User.uuid == ou,
                User.archived == False
            ).first()
        target_user = User.query.filter(
                User.uuid == tu,
                User.archived == False
            ).first()

        if originating_user and originating_user.valid() and target_user and target_user.valid() and originating_user.is_following(target_user.uuid):
            relationship = Follow().query\
                                .filter(Follow.originating_id == originating_user.uuid)\
                                .filter(Follow.target_id == target_user.uuid).first()
        else:
            relationship = None

        if relationship:
            db.session.delete(relationship)
            db.session.commit()
            return '{} successfully unfollowed {}'.format(ou, tu)
        else:
            return None

User.following = relationship(Follow,
                                foreign_keys=[Follow.originating_id],
                                backref='originating_user',
                                order_by=Follow.target_id,
                                lazy='dynamic',
                                cascade='all,delete,delete-orphan'
                            )
User.followers = relationship(Follow,
                                foreign_keys=[Follow.target_id],
                                backref='target_user',
                                order_by=Follow.originating_id,
                                lazy='dynamic',
                                cascade='all,delete,delete-orphan'
                            )

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

