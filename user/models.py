from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from app import db
from app.models import MediaObject
from app.utils import generate_uuid
from datetime import datetime
import uuid
import json

class User(UserMixin, MediaObject):
    # id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    # name = db.Column(db.String(64), index=True, unique=True)
    # uuid = db.Column(db.String(36), index=True, unique=True, default=generate_uuid)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    archived = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.name)
    
    def _to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'email': self.email,
            'archived': self.archived
        }
    
    def _get_archived(self):
        return {
            'id': self.id,
            'archived': self.archived
        }
    
    def valid(self):
        return False if self.archived else True
    
    def get(self):
        if self.archived:
            return self._get_archived()
        else:
            return self._to_dict()
    
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

    def delete(self):
        # TODO: implement delete method
        db.session.delete(self)
        db.session.commit()
        return
    
    def is_following(self, target_user_name):
        target_user = User.get(target_user_name)
        relationship = Follow.get(self.id, target_user.id)

        return True if relationship.one() else False


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    originating_user = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    target_user = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    label = db.Column(db.String)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

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


