"""
Deloitte Flask App Template
A clean starting point for Flask web applications with Deloitte branding.
"""
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import config
from models import db, User, AuditLog
from translations import get_translation as t


# ============================================================================
# APP INITIALIZATION
# ============================================================================

def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Bitte melden Sie sich an.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app


app = create_app()


# ============================================================================
# CONTEXT PROCESSORS
# ============================================================================

@app.context_processor
def inject_globals():
    """Inject global variables into all templates"""
    lang = session.get('lang', app.config.get('DEFAULT_LANGUAGE', 'de'))
    return {
        'app_name': app.config.get('APP_NAME', 'MyApp'),
        'app_version': app.config.get('APP_VERSION', '1.0.0'),
        'current_year': datetime.now().year,
        'lang': lang,
        't': lambda key: t(key, lang)
    }


# ============================================================================
# DECORATORS
# ============================================================================

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Keine Berechtigung für diese Aktion.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def log_action(action, entity_type=None, entity_id=None, entity_name=None, old_value=None, new_value=None):
    """Log an action to the audit log"""
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        old_value=old_value,
        new_value=new_value,
        ip_address=request.remote_addr,
        user_agent=str(request.user_agent)[:500] if request.user_agent else None
    )
    db.session.add(log)
    db.session.commit()


# ============================================================================
# AUTH ROUTES
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Ihr Konto ist deaktiviert.', 'danger')
                return render_template('login.html')
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_action('LOGIN', 'User', user.id, user.email)
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('Ungültige Anmeldedaten.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    log_action('LOGOUT', 'User', current_user.id, current_user.email)
    logout_user()
    flash('Sie wurden abgemeldet.', 'success')
    return redirect(url_for('index'))


# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/set-language/<lang>')
def set_language(lang):
    """Change language"""
    if lang in app.config.get('SUPPORTED_LANGUAGES', ['de', 'en']):
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


# ============================================================================
# ADMIN ROUTES
# ============================================================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    stats = {
        'users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
    }
    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/users')
@admin_required
def admin_users():
    """User management"""
    users = User.query.order_by(User.name).all()
    return render_template('admin/users.html', users=users)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ============================================================================
# CLI COMMANDS
# ============================================================================

@app.cli.command()
def initdb():
    """Initialize the database"""
    db.create_all()
    print('Database initialized.')


@app.cli.command()
def createadmin():
    """Create admin user"""
    admin = User(
        email='admin@example.com',
        name='Administrator',
        role='admin',
        is_active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created: admin@example.com / admin123')


# ============================================================================
# RUN
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
