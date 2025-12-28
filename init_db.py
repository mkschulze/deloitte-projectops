"""
Deloitte Flask App Template - Database Initialization
Run: python init_db.py
"""
from app import app, db
from models import User


def init_database():
    """Initialize database with tables and default admin user"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print('✓ Database tables created')
        
        # Check if admin exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                name='Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✓ Admin user created: admin@example.com / admin123')
        else:
            print('• Admin user already exists')
        
        # Create demo user
        user = User.query.filter_by(email='user@example.com').first()
        if not user:
            user = User(
                email='user@example.com',
                name='Demo User',
                role='user',
                is_active=True
            )
            user.set_password('user123')
            db.session.add(user)
            db.session.commit()
            print('✓ Demo user created: user@example.com / user123')
        else:
            print('• Demo user already exists')
        
        print('\n🚀 Database initialized successfully!')
        print('   Run: flask run --debug')


if __name__ == '__main__':
    init_database()
