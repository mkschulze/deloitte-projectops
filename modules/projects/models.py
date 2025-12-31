"""
Project Management Module - Database Models
"""
from datetime import datetime
from enum import Enum

from extensions import db


class ProjectRole(Enum):
    """Project member role enumeration"""
    ADMIN = 'admin'      # Full project control
    LEAD = 'lead'        # Can manage issues, sprints
    MEMBER = 'member'    # Can work on issues
    VIEWER = 'viewer'    # Read-only access
    
    @classmethod
    def choices(cls):
        return [(role.value, role.name.title()) for role in cls]


class Project(db.Model):
    """Project model for grouping issues"""
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(10), unique=True, nullable=False, index=True)  # TAX, AUD, HR
    name = db.Column(db.String(200), nullable=False)
    name_en = db.Column(db.String(200))  # English name (optional)
    description = db.Column(db.Text)
    description_en = db.Column(db.Text)  # English description (optional)
    
    # Project lead
    lead_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Categorization
    category = db.Column(db.String(50))  # e.g., 'tax', 'audit', 'consulting'
    icon = db.Column(db.String(50), default='bi-folder')  # Bootstrap icon
    color = db.Column(db.String(7), default='#86BC25')  # Hex color for badges
    
    # Status
    is_archived = db.Column(db.Boolean, default=False)
    archived_at = db.Column(db.DateTime)
    
    # Issue counter for auto-incrementing issue keys
    issue_counter = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    lead = db.relationship('User', foreign_keys=[lead_id], backref='led_projects')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    members = db.relationship('ProjectMember', back_populates='project', cascade='all, delete-orphan')
    
    def get_name(self, lang='de'):
        """Get localized name"""
        if lang == 'en' and self.name_en:
            return self.name_en
        return self.name
    
    def get_description(self, lang='de'):
        """Get localized description"""
        if lang == 'en' and self.description_en:
            return self.description_en
        return self.description or ''
    
    def get_next_issue_key(self):
        """Generate next issue key (e.g., TAX-42)"""
        self.issue_counter += 1
        return f"{self.key}-{self.issue_counter}"
    
    def is_member(self, user):
        """Check if user is a member of this project"""
        if user.role == 'admin':
            return True
        return any(m.user_id == user.id for m in self.members)
    
    def get_member_role(self, user):
        """Get user's role in this project"""
        if user.role == 'admin':
            return 'admin'
        for m in self.members:
            if m.user_id == user.id:
                return m.role
        return None
    
    def can_user_edit(self, user):
        """Check if user can edit project settings"""
        role = self.get_member_role(user)
        return role in ['admin', 'lead']
    
    def can_user_manage_issues(self, user):
        """Check if user can create/edit issues"""
        role = self.get_member_role(user)
        return role in ['admin', 'lead', 'member']
    
    @property
    def member_count(self):
        """Get number of members"""
        return len(self.members)
    
    def __repr__(self):
        return f'<Project {self.key}: {self.name}>'


class ProjectMember(db.Model):
    """Project membership with role"""
    __tablename__ = 'project_member'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # admin, lead, member, viewer
    
    # Timestamps
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    project = db.relationship('Project', back_populates='members')
    user = db.relationship('User', foreign_keys=[user_id], backref='project_memberships')
    added_by = db.relationship('User', foreign_keys=[added_by_id])
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'user_id', name='unique_project_member'),
    )
    
    def get_role_display(self, lang='de'):
        """Get localized role display name"""
        roles_de = {
            'admin': 'Administrator',
            'lead': 'Projektleiter',
            'member': 'Mitglied',
            'viewer': 'Beobachter'
        }
        roles_en = {
            'admin': 'Administrator',
            'lead': 'Project Lead',
            'member': 'Member',
            'viewer': 'Viewer'
        }
        roles = roles_de if lang == 'de' else roles_en
        return roles.get(self.role, self.role)
    
    def __repr__(self):
        return f'<ProjectMember {self.user_id} in {self.project_id} as {self.role}>'
