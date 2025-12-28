"""
Deloitte TaxOps Calendar - Database Models
"""
from datetime import datetime, date
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ============================================================================
# ASSOCIATION TABLES
# ============================================================================

class TaskReviewer(db.Model):
    """Association table for Task-Reviewer many-to-many with approval tracking"""
    __tablename__ = 'task_reviewer'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order = db.Column(db.Integer, default=1)  # Order in approval chain
    
    # Approval tracking
    has_approved = db.Column(db.Boolean, default=False)
    approved_at = db.Column(db.DateTime)
    approval_note = db.Column(db.Text)
    
    # Rejection tracking
    has_rejected = db.Column(db.Boolean, default=False)
    rejected_at = db.Column(db.DateTime)
    rejection_note = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='reviewer_assignments')
    
    __table_args__ = (
        db.UniqueConstraint('task_id', 'user_id', name='unique_task_reviewer'),
    )
    
    def approve(self, note=None):
        """Mark this reviewer's approval"""
        self.has_approved = True
        self.approved_at = datetime.utcnow()
        self.approval_note = note
        self.has_rejected = False
        self.rejected_at = None
        self.rejection_note = None
    
    def reject(self, note=None):
        """Mark this reviewer's rejection"""
        self.has_rejected = True
        self.rejected_at = datetime.utcnow()
        self.rejection_note = note
        self.has_approved = False
        self.approved_at = None
        self.approval_note = None
    
    def reset(self):
        """Reset approval/rejection status"""
        self.has_approved = False
        self.approved_at = None
        self.approval_note = None
        self.has_rejected = False
        self.rejected_at = None
        self.rejection_note = None


# ============================================================================
# ENUMS
# ============================================================================

class TaskStatus(Enum):
    """Task status enumeration"""
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    IN_REVIEW = 'in_review'
    COMPLETED = 'completed'
    
    @classmethod
    def choices(cls):
        return [(status.value, status.name.replace('_', ' ').title()) for status in cls]


class UserRole(Enum):
    """User role enumeration"""
    ADMIN = 'admin'
    MANAGER = 'manager'
    REVIEWER = 'reviewer'
    PREPARER = 'preparer'
    READONLY = 'readonly'
    
    @classmethod
    def choices(cls):
        return [(role.value, role.name.title()) for role in cls]


class EvidenceType(Enum):
    """Evidence type enumeration"""
    FILE = 'file'
    LINK = 'link'


class RecurrenceType(Enum):
    """Task recurrence type"""
    NONE = 'none'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    ANNUAL = 'annual'


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='preparer')  # admin, manager, reviewer, preparer, readonly
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    owned_tasks = db.relationship('Task', foreign_keys='Task.owner_id', backref='owner', lazy='dynamic')
    reviewed_tasks = db.relationship('Task', foreign_keys='Task.reviewer_id', backref='reviewer', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    def is_manager(self):
        """Check if user has manager role"""
        return self.role in ('admin', 'manager')
    
    def can_review(self):
        """Check if user can review tasks"""
        return self.role in ('admin', 'manager', 'reviewer')
    
    def __repr__(self):
        return f'<User {self.email}>'


class AuditLog(db.Model):
    """Audit log for tracking changes"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    entity_name = db.Column(db.String(200))
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    
    # Relationships
    user = db.relationship('User', backref='audit_logs', lazy=True)
    
    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity_type}>'


# ============================================================================
# ADD YOUR CUSTOM MODELS BELOW
# ============================================================================


class Entity(db.Model):
    """Legal entity (Gesellschaft) for tax compliance"""
    __tablename__ = 'entity'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    short_name = db.Column(db.String(50))
    country = db.Column(db.String(5), default='DE')  # ISO country code
    group_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for entity groups
    children = db.relationship('Entity', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    tasks = db.relationship('Task', backref='entity', lazy='dynamic')
    
    def __repr__(self):
        return f'<Entity {self.name}>'


class TaxType(db.Model):
    """Tax type catalog (Steuerart)"""
    __tablename__ = 'tax_type'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # KSt, USt, GewSt
    name = db.Column(db.String(100), nullable=False)  # Körperschaftsteuer
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    templates = db.relationship('TaskTemplate', backref='tax_type', lazy='dynamic')
    
    def __repr__(self):
        return f'<TaxType {self.code}>'


class TaskTemplate(db.Model):
    """Task template for generating recurring tasks"""
    __tablename__ = 'task_template'
    
    id = db.Column(db.Integer, primary_key=True)
    tax_type_id = db.Column(db.Integer, db.ForeignKey('tax_type.id'), nullable=False)
    keyword = db.Column(db.String(100), nullable=False)  # Short identifier
    description = db.Column(db.Text)
    default_recurrence = db.Column(db.String(20), default='annual')  # none, monthly, quarterly, annual
    default_due_day = db.Column(db.Integer, default=15)  # Day of month
    default_due_month_offset = db.Column(db.Integer, default=0)  # Months after period end
    source_row = db.Column(db.Integer)  # Row number from Excel import
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    tasks = db.relationship('Task', backref='template', lazy='dynamic')
    
    def __repr__(self):
        return f'<TaskTemplate {self.keyword}>'


class TaskPreset(db.Model):
    """Predefined task templates for quick task creation (Aufgabenvorlagen)"""
    __tablename__ = 'task_preset'
    
    CATEGORIES = ['antrag', 'aufgabe']
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False, default='aufgabe')  # antrag, aufgabe
    tax_type = db.Column(db.String(100))  # Steuerart (free text, more flexible than FK)
    title = db.Column(db.String(300), nullable=False)  # Aufgabe / Zweck des Antrags
    law_reference = db.Column(db.String(100))  # § Paragraph (for Anträge)
    description = db.Column(db.Text)  # Erläuterung
    source = db.Column(db.String(50))  # Import source: 'json', 'excel', 'manual'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TaskPreset {self.title[:30]}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON export"""
        return {
            'id': self.id,
            'category': self.category,
            'tax_type': self.tax_type,
            'title': self.title,
            'law_reference': self.law_reference,
            'description': self.description,
            'is_active': self.is_active
        }


class Task(db.Model):
    """Individual task instance (calendar item)"""
    __tablename__ = 'task'
    
    # Status workflow: draft -> submitted -> in_review -> approved -> completed
    # Or can be rejected back to draft at any stage
    VALID_STATUSES = ['draft', 'submitted', 'in_review', 'approved', 'completed', 'rejected']
    
    # Status transitions: current_status -> [allowed next statuses]
    STATUS_TRANSITIONS = {
        'draft': ['submitted'],
        'submitted': ['in_review', 'rejected'],
        'in_review': ['approved', 'rejected'],
        'approved': ['completed', 'rejected'],
        'completed': [],  # Final state
        'rejected': ['draft'],  # Can restart
    }
    
    # Who can perform which transitions
    STATUS_PERMISSIONS = {
        'draft->submitted': ['owner', 'preparer', 'manager', 'admin'],
        'submitted->in_review': ['reviewer', 'manager', 'admin'],
        'submitted->rejected': ['reviewer', 'manager', 'admin'],
        'in_review->approved': ['manager', 'admin'],
        'in_review->rejected': ['reviewer', 'manager', 'admin'],
        'approved->completed': ['manager', 'admin'],
        'approved->rejected': ['manager', 'admin'],
        'rejected->draft': ['owner', 'preparer', 'manager', 'admin'],
    }
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('task_template.id'), nullable=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    period = db.Column(db.String(10))  # Q1, Q2, Q3, Q4, M01-M12, or empty for annual
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False, index=True)
    
    status = db.Column(db.String(20), default='draft', index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Legacy single reviewer (optional)
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Manager who approves
    
    # Workflow timestamps
    submitted_at = db.Column(db.DateTime)
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    completed_at = db.Column(db.DateTime)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    rejected_at = db.Column(db.DateTime)
    rejected_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    rejection_reason = db.Column(db.Text)
    
    completion_note = db.Column(db.Text)  # What was filed, where, by whom
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    evidence = db.relationship('TaskEvidence', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    
    # Multi-reviewer relationship
    reviewers = db.relationship('TaskReviewer', backref='task', lazy='dynamic', 
                                cascade='all, delete-orphan', order_by='TaskReviewer.order')
    
    # Additional user relationships for workflow
    submitted_by = db.relationship('User', foreign_keys=[submitted_by_id], backref='tasks_submitted')
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id], backref='tasks_reviewed_by')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='tasks_approved')
    completed_by = db.relationship('User', foreign_keys=[completed_by_id], backref='tasks_completed')
    rejected_by = db.relationship('User', foreign_keys=[rejected_by_id], backref='tasks_rejected')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='tasks_to_approve')
    
    # =========================================================================
    # MULTI-REVIEWER METHODS
    # =========================================================================
    
    def get_reviewer_users(self):
        """Get list of reviewer User objects"""
        return [tr.user for tr in self.reviewers.all()]
    
    def get_reviewer_ids(self):
        """Get list of reviewer user IDs"""
        return [tr.user_id for tr in self.reviewers.all()]
    
    def add_reviewer(self, user, order=None):
        """Add a reviewer to this task"""
        existing = TaskReviewer.query.filter_by(task_id=self.id, user_id=user.id).first()
        if existing:
            return existing
        if order is None:
            max_order = db.session.query(db.func.max(TaskReviewer.order)).filter_by(task_id=self.id).scalar() or 0
            order = max_order + 1
        tr = TaskReviewer(task_id=self.id, user_id=user.id, order=order)
        db.session.add(tr)
        return tr
    
    def remove_reviewer(self, user):
        """Remove a reviewer from this task"""
        TaskReviewer.query.filter_by(task_id=self.id, user_id=user.id).delete()
    
    def set_reviewers(self, user_ids):
        """Set reviewers from list of user IDs (replaces existing)"""
        # Remove all existing
        TaskReviewer.query.filter_by(task_id=self.id).delete()
        # Add new ones
        for i, user_id in enumerate(user_ids, 1):
            tr = TaskReviewer(task_id=self.id, user_id=user_id, order=i)
            db.session.add(tr)
    
    def get_reviewer_status(self, user):
        """Get approval status for a specific reviewer"""
        tr = TaskReviewer.query.filter_by(task_id=self.id, user_id=user.id).first()
        if not tr:
            return None
        if tr.has_approved:
            return 'approved'
        if tr.has_rejected:
            return 'rejected'
        return 'pending'
    
    def approve_by_reviewer(self, user, note=None):
        """Record approval by a specific reviewer"""
        tr = TaskReviewer.query.filter_by(task_id=self.id, user_id=user.id).first()
        if tr:
            tr.approve(note)
            return True
        return False
    
    def reject_by_reviewer(self, user, note=None):
        """Record rejection by a specific reviewer"""
        tr = TaskReviewer.query.filter_by(task_id=self.id, user_id=user.id).first()
        if tr:
            tr.reject(note)
            return True
        return False
    
    def reset_all_approvals(self):
        """Reset all reviewer approvals (e.g., when resubmitting)"""
        for tr in self.reviewers.all():
            tr.reset()
    
    def get_approval_count(self):
        """Get count of approved vs total reviewers"""
        total = self.reviewers.count()
        approved = self.reviewers.filter_by(has_approved=True).count()
        return approved, total
    
    def all_reviewers_approved(self):
        """Check if all assigned reviewers have approved"""
        total = self.reviewers.count()
        if total == 0:
            return True  # No reviewers required
        approved = self.reviewers.filter_by(has_approved=True).count()
        return approved >= total
    
    def any_reviewer_rejected(self):
        """Check if any reviewer has rejected"""
        return self.reviewers.filter_by(has_rejected=True).count() > 0
    
    def is_reviewer(self, user):
        """Check if user is a reviewer for this task"""
        return TaskReviewer.query.filter_by(task_id=self.id, user_id=user.id).count() > 0
    
    def get_pending_reviewers(self):
        """Get reviewers who haven't approved or rejected yet"""
        return self.reviewers.filter_by(has_approved=False, has_rejected=False).all()
    
    def can_transition_to(self, new_status, user):
        """Check if user can transition task to new status"""
        if new_status not in self.STATUS_TRANSITIONS.get(self.status, []):
            return False
        
        transition_key = f"{self.status}->{new_status}"
        allowed_roles = self.STATUS_PERMISSIONS.get(transition_key, [])
        
        # Check user role
        if user.role in ['admin', 'manager']:
            return True
        if 'owner' in allowed_roles and self.owner_id == user.id:
            return True
        # Check multi-reviewer permissions
        if 'reviewer' in allowed_roles and self.is_reviewer(user):
            return True
        # Legacy single reviewer check
        if 'reviewer' in allowed_roles and self.reviewer_id == user.id:
            return True
        if user.role in allowed_roles:
            return True
        
        return False
    
    def get_allowed_transitions(self, user):
        """Get list of statuses user can transition to"""
        allowed = []
        for next_status in self.STATUS_TRANSITIONS.get(self.status, []):
            if self.can_transition_to(next_status, user):
                allowed.append(next_status)
        return allowed
    
    def transition_to(self, new_status, user, note=None):
        """Perform status transition with timestamp and user tracking"""
        if not self.can_transition_to(new_status, user):
            raise ValueError(f"Transition from {self.status} to {new_status} not allowed for user {user.email}")
        
        old_status = self.status
        self.status = new_status
        now = datetime.utcnow()
        
        if new_status == 'submitted':
            self.submitted_at = now
            self.submitted_by_id = user.id
        elif new_status == 'in_review':
            self.reviewed_at = now
            self.reviewed_by_id = user.id
        elif new_status == 'approved':
            self.approved_at = now
            self.approved_by_id = user.id
        elif new_status == 'completed':
            self.completed_at = now
            self.completed_by_id = user.id
            if note:
                self.completion_note = note
        elif new_status == 'rejected':
            self.rejected_at = now
            self.rejected_by_id = user.id
            if note:
                self.rejection_reason = note
        elif new_status == 'draft':
            # Reset rejection when restarting
            self.rejection_reason = None
        
        return old_status
    
    @property
    def workflow_progress(self):
        """Get workflow progress percentage"""
        progress_map = {
            'draft': 0,
            'submitted': 25,
            'in_review': 50,
            'approved': 75,
            'completed': 100,
            'rejected': 10,
        }
        return progress_map.get(self.status, 0)
    
    @property
    def next_action_by(self):
        """Who needs to take action next"""
        if self.status == 'draft':
            return self.owner
        elif self.status == 'submitted':
            return self.reviewer
        elif self.status == 'in_review':
            return self.approver or self.reviewer
        elif self.status == 'approved':
            return self.approver or self.owner
        elif self.status == 'rejected':
            return self.owner
        return None
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.status == 'completed':
            return False
        return self.due_date < date.today()
    
    @property
    def is_due_soon(self, days=7):
        """Check if task is due within N days"""
        if self.status == 'completed':
            return False
        delta = (self.due_date - date.today()).days
        return 0 <= delta <= days
    
    @property
    def effective_status(self):
        """Get effective status including automatic overlays"""
        if self.status == 'completed':
            return 'completed'
        if self.is_overdue:
            return 'overdue'
        if self.is_due_soon:
            return 'due_soon'
        return self.status
    
    def __repr__(self):
        return f'<Task {self.title} ({self.due_date})>'


class TaskEvidence(db.Model):
    """Evidence attached to a task (files or links)"""
    __tablename__ = 'task_evidence'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    evidence_type = db.Column(db.String(10), nullable=False)  # file, link
    
    # For files
    filename = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    # For links
    url = db.Column(db.String(500))
    link_title = db.Column(db.String(200))
    
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    uploaded_by = db.relationship('User', backref='uploaded_evidence')
    
    def __repr__(self):
        return f'<TaskEvidence {self.evidence_type}: {self.filename or self.url}>'


class Comment(db.Model):
    """Comments on tasks or references"""
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    reference_id = db.Column(db.Integer, db.ForeignKey('reference_application.id'), nullable=True)
    
    text = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)
    
    created_by = db.relationship('User', backref='comments')
    
    def __repr__(self):
        return f'<Comment {self.id} by {self.created_by_id}>'


class ReferenceApplication(db.Model):
    """Reference library for law-based applications (Anträge)"""
    __tablename__ = 'reference_application'
    
    id = db.Column(db.Integer, primary_key=True)
    law = db.Column(db.String(100))  # e.g., "EStG", "KStG"
    paragraph = db.Column(db.String(50))  # e.g., "§ 34a"
    title = db.Column(db.String(200), nullable=False)
    purpose = db.Column(db.Text)
    explanation = db.Column(db.Text)
    deadline_info = db.Column(db.Text)  # When to apply
    source = db.Column(db.String(100))  # Which Excel sheet/import
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    comments = db.relationship('Comment', backref='reference', lazy='dynamic')
    
    def __repr__(self):
        return f'<ReferenceApplication {self.law} {self.paragraph}>'


# ============================================================================
# ASSOCIATION TABLES
# ============================================================================

# Entity-User permissions (which users can access which entities)
entity_user_access = db.Table('entity_user_access',
    db.Column('entity_id', db.Integer, db.ForeignKey('entity.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)
