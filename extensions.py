"""
Flask Extensions
Central initialization of all Flask extensions.
"""
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Database
db = SQLAlchemy()

# CSRF Protection
csrf = CSRFProtect()

# Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute"],  # Default rate limit
    storage_uri="memory://",  # Use in-memory storage
)

# Migrations
migrate = Migrate()

# SocketIO for real-time features
socketio = SocketIO()

# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bitte melden Sie sich an.'
login_manager.login_message_category = 'warning'
