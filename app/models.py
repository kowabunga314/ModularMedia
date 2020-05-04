from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from app import db
from app.utils import generate_uuid
from datetime import datetime
import uuid
import json


class MediaAbstract(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return

class MediaObject(MediaAbstract):
    __abstract__ = True
    name = db.Column(db.String(64))
    uuid = db.Column(db.String(36), index=True, unique=True, default=generate_uuid)
    archived = db.Column(db.Boolean, default=False)

    def __init__(self, name=None):
        self.name = name
    
    def _get_archived(self):
        return {
            'id': self.id,
            'archived': self.archived
        }
    
    def valid(self):
        return False if self.archived else True
