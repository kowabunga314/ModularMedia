import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Some basic app & DB config stuff
    #   most config should live in the DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False