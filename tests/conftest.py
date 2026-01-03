"""
Pytest configuration and fixtures for Deloitte ProjectOps.
"""
import os
import sys
import pytest
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_login import login_user

from extensions import db as _db
from app import create_app
from config import Config


class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost'
    SECRET_KEY = 'test-secret-key'
    LOGIN_DISABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    _app = create_app('testing')
    _app.config.from_object(TestConfig)
    
    # Create application context
    ctx = _app.app_context()
    ctx.push()
    
    yield _app
    
    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    """Create database for testing."""
    _db.app = app
    _db.create_all()
    
    yield _db
    
    _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """Create a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Create session bound to this connection
    options = dict(bind=connection, binds={})
    session = db._make_scoped_session(options=options)
    
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture(scope='function')
def client(app, db):
    """Create test client."""
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(scope='function')
def runner(app):
    """Create CLI test runner."""
    return app.test_cli_runner()


# =============================================================================
# USER FIXTURES
# =============================================================================

@pytest.fixture
def user(db):
    """Create a test user."""
    from models import User
    
    user = User(
        email='test@example.com',
        name='Test User',
        role='preparer',
        is_active=True
    )
    user.set_password('testpassword123')
    
    db.session.add(user)
    db.session.commit()
    
    yield user
    
    # Cleanup
    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    from models import User
    
    admin = User(
        email='admin@example.com',
        name='Admin User',
        role='admin',
        is_active=True
    )
    admin.set_password('adminpassword123')
    
    db.session.add(admin)
    db.session.commit()
    
    yield admin
    
    db.session.delete(admin)
    db.session.commit()


@pytest.fixture
def authenticated_client(client, user, app):
    """Client with authenticated user."""
    with app.test_request_context():
        login_user(user)
    
    with client.session_transaction() as sess:
        sess['_user_id'] = user.id
        sess['_fresh'] = True
    
    yield client


# =============================================================================
# TENANT FIXTURES
# =============================================================================

@pytest.fixture
def tenant(db):
    """Create a test tenant."""
    from models import Tenant
    
    tenant = Tenant(
        name='Test Tenant',
        slug='test-tenant',
        is_active=True
    )
    
    db.session.add(tenant)
    db.session.commit()
    
    yield tenant
    
    db.session.delete(tenant)
    db.session.commit()


@pytest.fixture
def tenant_with_user(db, tenant, user):
    """Create tenant with user membership."""
    from models import TenantMembership
    
    membership = TenantMembership(
        tenant_id=tenant.id,
        user_id=user.id,
        role='member',
        is_default=True
    )
    
    db.session.add(membership)
    db.session.commit()
    
    yield tenant, user
    
    db.session.delete(membership)
    db.session.commit()


# =============================================================================
# PROJECT FIXTURES
# =============================================================================

@pytest.fixture
def project(db, tenant):
    """Create a test project."""
    from modules.projects.models import Project
    
    project = Project(
        name='Test Project',
        key='TEST',
        description='A test project',
        tenant_id=tenant.id,
        methodology='scrum'
    )
    
    db.session.add(project)
    db.session.commit()
    
    yield project
    
    db.session.delete(project)
    db.session.commit()


@pytest.fixture
def project_with_member(db, project, user):
    """Create project with team member."""
    from modules.projects.models import ProjectMember
    
    member = ProjectMember(
        project_id=project.id,
        user_id=user.id,
        role='member'
    )
    
    db.session.add(member)
    db.session.commit()
    
    yield project, user
    
    db.session.delete(member)
    db.session.commit()


@pytest.fixture
def sprint(db, project):
    """Create a test sprint."""
    from modules.projects.models import Sprint
    from datetime import timedelta
    
    sprint = Sprint(
        name='Sprint 1',
        project_id=project.id,
        start_date=datetime.utcnow().date(),
        end_date=(datetime.utcnow() + timedelta(days=14)).date(),
        goal='Complete sprint goals'
    )
    
    db.session.add(sprint)
    db.session.commit()
    
    yield sprint
    
    db.session.delete(sprint)
    db.session.commit()


@pytest.fixture
def issue_type(db, project):
    """Create a test issue type."""
    from modules.projects.models import IssueType
    
    issue_type = IssueType(
        name='Task',
        project_id=project.id,
        icon='bi-check-square',
        color='#0076A8'
    )
    
    db.session.add(issue_type)
    db.session.commit()
    
    yield issue_type
    
    db.session.delete(issue_type)
    db.session.commit()


@pytest.fixture
def issue_status(db, project):
    """Create a test issue status."""
    from modules.projects.models import IssueStatus
    
    status = IssueStatus(
        name='To Do',
        project_id=project.id,
        category='todo',
        sort_order=1,
        is_initial=True
    )
    
    db.session.add(status)
    db.session.commit()
    
    yield status
    
    db.session.delete(status)
    db.session.commit()


@pytest.fixture
def issue(db, project, issue_type, issue_status, user, tenant):
    """Create a test issue."""
    from modules.projects.models import Issue
    
    issue = Issue(
        key=f'{project.key}-1',
        summary='Test Issue',
        description='Test issue description',
        project_id=project.id,
        tenant_id=tenant.id,
        type_id=issue_type.id,
        status_id=issue_status.id,
        reporter_id=user.id
    )
    
    db.session.add(issue)
    db.session.commit()
    
    yield issue
    
    db.session.delete(issue)
    db.session.commit()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

@pytest.fixture
def login_as(client, app):
    """Factory fixture to log in as any user."""
    def _login_as(user):
        with client.session_transaction() as sess:
            sess['_user_id'] = user.id
            sess['_fresh'] = True
        return client
    
    return _login_as


@pytest.fixture
def set_tenant_context(app):
    """Factory fixture to set tenant context."""
    def _set_tenant(tenant):
        from flask import g
        g.current_tenant = tenant
    
    return _set_tenant


# =============================================================================
# API HELPERS
# =============================================================================

@pytest.fixture
def api_headers():
    """Standard API headers."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
