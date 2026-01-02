"""
Project Management Module - Database Models

Flexible Architecture:
- IssueType: Configurable per project (Epic, Story, Task, or custom)
- IssueStatus: Configurable workflows with category mapping
- Issue: Core work item with auto-generated keys
"""
from datetime import datetime
from enum import Enum

from extensions import db


# =============================================================================
# ENUMS (for category mapping, not for restricting types)
# =============================================================================

class StatusCategory(Enum):
    """Category for status mapping (used for reports/metrics)"""
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    
    @classmethod
    def choices(cls):
        return [(c.value, c.name.replace('_', ' ').title()) for c in cls]


class ProjectMethodology(Enum):
    """Project methodology template"""
    SCRUM = 'scrum'
    KANBAN = 'kanban'
    WATERFALL = 'waterfall'
    CUSTOM = 'custom'
    
    @classmethod
    def choices(cls):
        return [(m.value, m.name.title()) for m in cls]


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
    
    # Methodology & Configuration
    methodology = db.Column(db.String(20), default='scrum')  # scrum, kanban, waterfall, custom
    
    # Terminology overrides (JSON) - allows custom labels per project
    # Example: {"epic": "Initiative", "story": "Requirement", "sprint": "Iteration"}
    terminology = db.Column(db.JSON, default=dict)
    
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
    issue_types = db.relationship('IssueType', back_populates='project', cascade='all, delete-orphan')
    issue_statuses = db.relationship('IssueStatus', back_populates='project', cascade='all, delete-orphan')
    issues = db.relationship('Issue', back_populates='project', cascade='all, delete-orphan')
    
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
    
    def get_term(self, key, lang='de'):
        """Get terminology with project-specific override
        
        Args:
            key: Standard term (epic, story, task, sprint, backlog, etc.)
            lang: Language code
        
        Returns:
            Project-specific term or default
        """
        defaults = {
            'de': {
                'epic': 'Epic',
                'story': 'Story',
                'task': 'Aufgabe',
                'bug': 'Fehler',
                'subtask': 'Unteraufgabe',
                'sprint': 'Sprint',
                'backlog': 'Backlog',
                'board': 'Board',
                'issue': 'Issue'
            },
            'en': {
                'epic': 'Epic',
                'story': 'Story',
                'task': 'Task',
                'bug': 'Bug',
                'subtask': 'Sub-Task',
                'sprint': 'Sprint',
                'backlog': 'Backlog',
                'board': 'Board',
                'issue': 'Issue'
            }
        }
        
        # Check project terminology override
        if self.terminology and key in self.terminology:
            override = self.terminology[key]
            if isinstance(override, dict):
                return override.get(lang, override.get('de', key))
            return override
        
        # Return default
        return defaults.get(lang, defaults['de']).get(key, key)
    
    def get_default_issue_type(self):
        """Get the default issue type for this project"""
        return IssueType.query.filter_by(
            project_id=self.id,
            is_default=True
        ).first() or self.issue_types[0] if self.issue_types else None
    
    def get_initial_status(self):
        """Get the initial status for new issues"""
        return IssueStatus.query.filter_by(
            project_id=self.id,
            is_initial=True
        ).first() or self.issue_statuses[0] if self.issue_statuses else None
    
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


# =============================================================================
# CONFIGURABLE ISSUE TYPES (per project)
# =============================================================================

class IssueType(db.Model):
    """Configurable issue type per project (Epic, Story, Task, etc.)"""
    __tablename__ = 'issue_type'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # Type definition
    name = db.Column(db.String(50), nullable=False)  # "Epic", "Story", "Task"
    name_en = db.Column(db.String(50))  # English name
    description = db.Column(db.String(200))
    
    # Visual
    icon = db.Column(db.String(50), default='bi-card-checklist')  # Bootstrap icon
    color = db.Column(db.String(7), default='#86BC25')  # Hex color
    
    # Hierarchy (0 = top level like Epic, 1 = Story, 2 = Task, 3 = Sub-Task)
    hierarchy_level = db.Column(db.Integer, default=1)
    can_have_children = db.Column(db.Boolean, default=True)
    allowed_child_types = db.Column(db.JSON, default=list)  # List of type IDs that can be children
    
    # Behavior
    is_default = db.Column(db.Boolean, default=False)  # Default type for quick create
    is_subtask = db.Column(db.Boolean, default=False)  # Sub-task type
    
    # Ordering
    sort_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='issue_types')
    issues = db.relationship('Issue', back_populates='issue_type')
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'name', name='unique_issue_type_per_project'),
    )
    
    def get_name(self, lang='de'):
        """Get localized name"""
        if lang == 'en' and self.name_en:
            return self.name_en
        return self.name
    
    def __repr__(self):
        return f'<IssueType {self.name} in Project {self.project_id}>'


# =============================================================================
# CONFIGURABLE WORKFLOW STATUS (per project)
# =============================================================================

class IssueStatus(db.Model):
    """Configurable workflow status per project"""
    __tablename__ = 'issue_status'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    
    # Status definition
    name = db.Column(db.String(50), nullable=False)  # "Open", "In Progress", "Done"
    name_en = db.Column(db.String(50))  # English name
    description = db.Column(db.String(200))
    
    # Category mapping for reports/metrics
    category = db.Column(db.String(20), default='todo')  # todo, in_progress, done
    
    # Visual
    icon = db.Column(db.String(50))  # Optional icon
    color = db.Column(db.String(7), default='#75787B')  # Hex color
    
    # Workflow
    is_initial = db.Column(db.Boolean, default=False)  # Starting status for new issues
    is_final = db.Column(db.Boolean, default=False)  # End status (Done, Cancelled)
    allowed_transitions = db.Column(db.JSON, default=list)  # List of status IDs that can transition to
    
    # Ordering (for board columns)
    sort_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='issue_statuses')
    issues = db.relationship('Issue', back_populates='status')
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'name', name='unique_status_per_project'),
    )
    
    def get_name(self, lang='de'):
        """Get localized name"""
        if lang == 'en' and self.name_en:
            return self.name_en
        return self.name
    
    def can_transition_to(self, target_status_id):
        """Check if transition to target status is allowed"""
        if not self.allowed_transitions:
            return True  # No restrictions = all transitions allowed
        return target_status_id in self.allowed_transitions
    
    def __repr__(self):
        return f'<IssueStatus {self.name} ({self.category}) in Project {self.project_id}>'


# =============================================================================
# ISSUE MODEL (Core work item)
# =============================================================================

class Issue(db.Model):
    """Issue/work item - the core entity for project work"""
    __tablename__ = 'issue'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    
    # Auto-generated key (TAX-1, TAX-2, etc.)
    key = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Issue type (Epic, Story, Task, etc.)
    type_id = db.Column(db.Integer, db.ForeignKey('issue_type.id'), nullable=False)
    
    # Workflow status
    status_id = db.Column(db.Integer, db.ForeignKey('issue_status.id'), nullable=False)
    
    # Content
    summary = db.Column(db.String(500), nullable=False)  # Title/summary
    description = db.Column(db.Text)  # Markdown description
    
    # Hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey('issue.id'), index=True)  # Parent issue (for sub-tasks)
    
    # Assignment
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Priority (1=Highest, 2=High, 3=Medium, 4=Low, 5=Lowest)
    priority = db.Column(db.Integer, default=3)
    
    # Time tracking
    original_estimate = db.Column(db.Integer)  # in minutes
    time_spent = db.Column(db.Integer, default=0)  # in minutes
    remaining_estimate = db.Column(db.Integer)  # in minutes
    
    # Dates
    due_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    resolution_date = db.Column(db.DateTime)  # When moved to final status
    
    # Sprint/Iteration (optional, for Scrum)
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprint.id'), index=True)
    
    # Story points (for Scrum estimation)
    story_points = db.Column(db.Float)
    
    # Labels (JSON array of strings)
    labels = db.Column(db.JSON, default=list)
    
    # Custom fields (JSON object for flexible data)
    custom_fields = db.Column(db.JSON, default=dict)
    
    # Board position (for Kanban ordering within a column)
    board_position = db.Column(db.Integer, default=0)
    
    # Backlog position (for prioritization)
    backlog_position = db.Column(db.Integer, default=0)
    
    # Archival
    is_archived = db.Column(db.Boolean, default=False)
    archived_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='issues')
    issue_type = db.relationship('IssueType', back_populates='issues')
    status = db.relationship('IssueStatus', back_populates='issues')
    parent = db.relationship('Issue', remote_side=[id], backref='children')
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_issues')
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reported_issues')
    # sprint relationship will be added when Sprint model is created
    
    def get_priority_display(self, lang='de'):
        """Get priority display name"""
        priorities = {
            1: ('Höchste', 'Highest'),
            2: ('Hoch', 'High'),
            3: ('Mittel', 'Medium'),
            4: ('Niedrig', 'Low'),
            5: ('Niedrigste', 'Lowest')
        }
        idx = 0 if lang == 'de' else 1
        return priorities.get(self.priority, ('Mittel', 'Medium'))[idx]
    
    def get_priority_icon(self):
        """Get priority icon class"""
        icons = {
            1: 'bi-chevron-double-up text-danger',
            2: 'bi-chevron-up text-danger',
            3: 'bi-dash text-warning',
            4: 'bi-chevron-down text-success',
            5: 'bi-chevron-double-down text-success'
        }
        return icons.get(self.priority, 'bi-dash text-warning')
    
    def format_time(self, minutes):
        """Format minutes as readable time (e.g., '2h 30m')"""
        if not minutes:
            return '-'
        hours = minutes // 60
        mins = minutes % 60
        if hours and mins:
            return f'{hours}h {mins}m'
        elif hours:
            return f'{hours}h'
        else:
            return f'{mins}m'
    
    @property
    def time_spent_display(self):
        return self.format_time(self.time_spent)
    
    @property
    def original_estimate_display(self):
        return self.format_time(self.original_estimate)
    
    @property
    def remaining_estimate_display(self):
        return self.format_time(self.remaining_estimate)
    
    @property
    def progress_percent(self):
        """Calculate progress based on time tracking"""
        if not self.original_estimate:
            return 0
        return min(100, int((self.time_spent / self.original_estimate) * 100))
    
    @property
    def is_overdue(self):
        """Check if issue is past due date and not done"""
        if not self.due_date or not self.status:
            return False
        if self.status.is_final:
            return False
        return self.due_date < datetime.utcnow().date()
    
    def __repr__(self):
        return f'<Issue {self.key}: {self.summary[:30]}>'


# =============================================================================
# SPRINT MODEL (for Scrum projects)
# =============================================================================

class Sprint(db.Model):
    """Sprint/Iteration for time-boxed work (Scrum)"""
    __tablename__ = 'sprint'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False, index=True)
    
    # Sprint info
    name = db.Column(db.String(100), nullable=False)  # "Sprint 1", "Sprint 2"
    goal = db.Column(db.Text)  # Sprint goal
    
    # Dates
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    # State
    state = db.Column(db.String(20), default='future')  # future, active, closed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    project = db.relationship('Project', backref='sprints')
    issues = db.relationship('Issue', backref='sprint', foreign_keys=[Issue.sprint_id])
    
    @property
    def is_active(self):
        return self.state == 'active'
    
    @property
    def total_points(self):
        """Sum of story points in sprint"""
        return sum(i.story_points or 0 for i in self.issues)
    
    @property
    def completed_points(self):
        """Sum of story points for done issues"""
        return sum(
            i.story_points or 0 
            for i in self.issues 
            if i.status and i.status.is_final
        )
    
    def __repr__(self):
        return f'<Sprint {self.name} ({self.state})>'


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def create_default_issue_types(project):
    """Create default issue types for a new project based on methodology"""
    
    scrum_types = [
        {'name': 'Epic', 'name_en': 'Epic', 'icon': 'bi-lightning-charge', 'color': '#6E2B62', 
         'hierarchy_level': 0, 'can_have_children': True, 'sort_order': 1},
        {'name': 'Story', 'name_en': 'Story', 'icon': 'bi-bookmark', 'color': '#86BC25', 
         'hierarchy_level': 1, 'can_have_children': True, 'is_default': True, 'sort_order': 2},
        {'name': 'Aufgabe', 'name_en': 'Task', 'icon': 'bi-check2-square', 'color': '#0076A8', 
         'hierarchy_level': 2, 'can_have_children': True, 'sort_order': 3},
        {'name': 'Fehler', 'name_en': 'Bug', 'icon': 'bi-bug', 'color': '#DA291C', 
         'hierarchy_level': 2, 'can_have_children': True, 'sort_order': 4},
        {'name': 'Unteraufgabe', 'name_en': 'Sub-Task', 'icon': 'bi-card-list', 'color': '#75787B', 
         'hierarchy_level': 3, 'can_have_children': False, 'is_subtask': True, 'sort_order': 5},
    ]
    
    kanban_types = [
        {'name': 'Aufgabe', 'name_en': 'Task', 'icon': 'bi-check2-square', 'color': '#0076A8', 
         'hierarchy_level': 1, 'can_have_children': True, 'is_default': True, 'sort_order': 1},
        {'name': 'Fehler', 'name_en': 'Bug', 'icon': 'bi-bug', 'color': '#DA291C', 
         'hierarchy_level': 1, 'can_have_children': True, 'sort_order': 2},
    ]
    
    waterfall_types = [
        {'name': 'Phase', 'name_en': 'Phase', 'icon': 'bi-folder2', 'color': '#6E2B62', 
         'hierarchy_level': 0, 'can_have_children': True, 'sort_order': 1},
        {'name': 'Meilenstein', 'name_en': 'Milestone', 'icon': 'bi-flag', 'color': '#86BC25', 
         'hierarchy_level': 1, 'can_have_children': True, 'sort_order': 2},
        {'name': 'Arbeitspaket', 'name_en': 'Work Package', 'icon': 'bi-box', 'color': '#0076A8', 
         'hierarchy_level': 2, 'can_have_children': True, 'is_default': True, 'sort_order': 3},
    ]
    
    type_configs = {
        'scrum': scrum_types,
        'kanban': kanban_types,
        'waterfall': waterfall_types,
        'custom': scrum_types  # Default to Scrum for custom
    }
    
    types = type_configs.get(project.methodology, scrum_types)
    
    for t in types:
        issue_type = IssueType(project_id=project.id, **t)
        db.session.add(issue_type)
    
    return types


def create_default_issue_statuses(project):
    """Create default workflow statuses for a new project based on methodology"""
    
    scrum_statuses = [
        {'name': 'Offen', 'name_en': 'Open', 'category': 'todo', 'color': '#75787B', 
         'is_initial': True, 'sort_order': 1},
        {'name': 'In Bearbeitung', 'name_en': 'In Progress', 'category': 'in_progress', 'color': '#0076A8', 
         'sort_order': 2},
        {'name': 'In Prüfung', 'name_en': 'In Review', 'category': 'in_progress', 'color': '#6E2B62', 
         'sort_order': 3},
        {'name': 'Erledigt', 'name_en': 'Done', 'category': 'done', 'color': '#86BC25', 
         'is_final': True, 'sort_order': 4},
    ]
    
    kanban_statuses = [
        {'name': 'Backlog', 'name_en': 'Backlog', 'category': 'todo', 'color': '#75787B', 
         'is_initial': True, 'sort_order': 1},
        {'name': 'Bereit', 'name_en': 'Ready', 'category': 'todo', 'color': '#0076A8', 
         'sort_order': 2},
        {'name': 'In Arbeit', 'name_en': 'In Progress', 'category': 'in_progress', 'color': '#E87722', 
         'sort_order': 3},
        {'name': 'Prüfung', 'name_en': 'Review', 'category': 'in_progress', 'color': '#6E2B62', 
         'sort_order': 4},
        {'name': 'Fertig', 'name_en': 'Done', 'category': 'done', 'color': '#86BC25', 
         'is_final': True, 'sort_order': 5},
    ]
    
    waterfall_statuses = [
        {'name': 'Geplant', 'name_en': 'Planned', 'category': 'todo', 'color': '#75787B', 
         'is_initial': True, 'sort_order': 1},
        {'name': 'Aktiv', 'name_en': 'Active', 'category': 'in_progress', 'color': '#0076A8', 
         'sort_order': 2},
        {'name': 'Abgeschlossen', 'name_en': 'Completed', 'category': 'done', 'color': '#86BC25', 
         'is_final': True, 'sort_order': 3},
        {'name': 'Blockiert', 'name_en': 'Blocked', 'category': 'in_progress', 'color': '#DA291C', 
         'sort_order': 4},
    ]
    
    status_configs = {
        'scrum': scrum_statuses,
        'kanban': kanban_statuses,
        'waterfall': waterfall_statuses,
        'custom': scrum_statuses
    }
    
    statuses = status_configs.get(project.methodology, scrum_statuses)
    
    for s in statuses:
        status = IssueStatus(project_id=project.id, **s)
        db.session.add(status)
    
    return statuses