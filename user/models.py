from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from app import db
import uuid
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    archived = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User {}'.format(self.name)
    
    def _to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'archived': self.archived
        }
    
    def _get_archived(self):
        return {
            'id': self.id,
            'archived': self.archived
        }
    
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
