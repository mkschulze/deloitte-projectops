"""
Flask Extensions
Central initialization of all Flask extensions.
"""
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# Database
db = SQLAlchemy()

# Migrations
migrate = Migrate()

# SocketIO for real-time features
socketio = SocketIO()

# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'core.login'
login_manager.login_message = 'Bitte melden Sie sich an.'
login_manager.login_message_category = 'warning'
