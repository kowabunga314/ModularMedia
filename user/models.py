from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from app import db
from app.models import MediaAbstract, MediaObject
from app.utils import generate_uuid
from datetime import datetime
import uuid
import json

class User(UserMixin, MediaObject):
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.name)
    
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
    def get(id=None, uuid=None, username=None, email=None):
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
    
    def create(self, name, email, password1, password2):
        # Verify that passwords match
        if password1 != password2:
            msg = 'passwords do not match.'
            raise ValueError(msg)

        # Verify that name is unique
        if User.query.filter(User.name == name).count():
            raise ValueError('That username is already taken!')

        # Verify that email is unique
        if User.query.filter(User.email == email).count():
            raise ValueError('An account with that email already exists!')

        # Create the user
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password1)
        )
        db.session.add(user)
        db.session.commit()
        return(json.dumps({'success': user._to_dict()}))

    def update(self, name=None, email=None, password1=None, password2=None, archived=None):
        self.name = name or self.name
        self.email = email or self.email

        # Handle password change
        if password1 and password1 == password2:
            self.password = generate_password_hash(password1)

        self.archived = archived if archived is not None else self.archived

        db.session.commit()
        return self.get()
    
    def is_following(self, target_user_id):
        relationship = Follow.get(self.id, target_user_id)

        return True if relationship.one() else False
    
    def belongs_to_group(self, group_id):
        relationship = GroupMembership.query.filter(GroupMembership.member_id == self.id, GroupMembership.group_id == group_id)

        return True if relationship.one() else False


class Follow(MediaAbstract):
    originating_user = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    target_user = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    label = db.Column(db.String)

    def __repr__(self):
        return '{} {} {}'.format(self.originating_user, self.label, self.target_user)
    
    @staticmethod
    def get(ou_id, tu_id):
        relatiohship = Follow.query.filter(Follow.originating_user == ou_id, Follow.target_user == tu_id).first()

        if relatiohship:
            return relatiohship
        else:
            return None

    def get_following(self, user_id):
        relationships = Follow.query.filter(Follow.originating_user == user_id).all()
        target_users = [relationship.target_user for relationship in relationships]

        users = User.query.filter(User.id.in_(target_users)).all()

        return [user.get() for user in users]

    def get_followers(self, user_id):
        relationships = Follow.query.filter(Follow.target_user == user_id).all()
        originating_users = [relationship.originating_user for relationship in relationships]

        users = User.query.filter(User.id.in_(originating_users)).all()

        return [user.get() for user in users]

    def follow_user(self, ou, tu, label='following'):
        # TODO: move check for archived user into class method
        self.originating_user = ou
        self.target_user = tu
        self.label = label

        db.session.add(self)
        db.session.commit()

        return self.__repr__()

    def unfollow_user(self, ou, tu):
        relationship = Follow.query.filter(Follow.originating_user == ou, Follow.target_user == tu).first()

        if relationship:
            db.session.delete(relationship)
            db.session.commit()
            return '{} successfully unfollowed {}'.format(ou, tu)
        else:
            return None


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

    def create(self, name=None):
        pass

    def get_members(self):
        relationships = GroupMembership.query.filter(GroupMembership.group_id == self.id).all()
        member_ids = [r.member_id for r in relationships]
        members = User.query.filter(User.id.in_(member_ids)).all()
        return [m for m in members]


class GroupMembership(MediaAbstract):
    group_id = db.Column(db.ForeignKey('group.id'), index=True)
    member_id = db.Column(db.ForeignKey('user.id'), index=True)
    label = db.Column(db.String(32), default='belongs to')

    def __repr__(self):
        return '{} {} {}'.format(self.member_id, self.label, self.group_id)
    
    @staticmethod
    def get(group_id, member_id):
        relatiohship = Group.query.filter(Group.group_id == group_id, Group.member_id == member_id).first()

        if relatiohship:
            return relatiohship
        else:
            return None

