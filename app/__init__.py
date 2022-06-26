from flask import Flask
from .utils import configuration

# Flask object
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = configuration.SECRET_KEY

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
