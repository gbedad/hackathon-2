from flask import Flask
from .utils import configuration

# Flask object
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = configuration.SECRET_KEY

login_manager = LoginManager(flask_app)
bcrypt = Bcrypt(flask_app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# Database connection
db_info = {
    'host': 'localhost',
    'database': 'teaching_rooms',
    'user': 'geraldberrebi',
    'port': ''
}

flask_app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_info['user']}@{db_info['host']}/{db_info['database']}"

flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app, db)


from app import routes, forms, models
