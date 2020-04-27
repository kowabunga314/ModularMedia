from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from app import db
from app.utils import generate_uuid
from datetime import datetime
import uuid
import json

class MediaObject(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(64), index=True, unique=True)
    uuid = db.Column(db.String(36), index=True, unique=True, default=generate_uuid)
