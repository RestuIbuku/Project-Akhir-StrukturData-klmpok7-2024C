from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import datetime
 
app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = 'kunci-rahasia-aplikasi-anda'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app.model import user, package 
from app import routes

@login_manager.user_loader
def load_user(id):
    return user.User.query.get(int(id))

@app.template_filter('strftime')
def _jinja2_filter_datetime(date_str, fmt=None):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    native = date_obj.replace(tzinfo=None)
    format='%d %B %Y'
    return native.strftime(format)