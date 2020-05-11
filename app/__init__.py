from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    env = os.environ.get('ENV', 'DEV')

    app.config['SECRET_KEY'] = 'Dingobaby68+1' #this needs to be removed 
    if env == 'DOCKER':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(Config.BASE_DIR, 'data', 'db.sqlite')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(Config.BASE_DIR, 'db.sqlite')

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from user.models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for user app
    from user.app import user as user_blueprint
    app.register_blueprint(user_blueprint)

    return app

