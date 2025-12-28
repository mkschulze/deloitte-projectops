# Technical Context

> Development environment, dependencies, and project structure for Deloitte TaxOps Calendar

## Tech Stack

### Backend

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | Flask 2.x | Web application framework |
| **ORM** | SQLAlchemy (Flask-SQLAlchemy) | Database abstraction |
| **Migrations** | Alembic (Flask-Migrate) | Schema version control |
| **Authentication** | Flask-Login | Session management |
| **Forms** | Flask-WTF + WTForms | Form handling & CSRF |
| **Password Hashing** | Werkzeug | Secure password storage |
| **Excel Processing** | openpyxl | Import/export Excel files |
| **Environment** | python-dotenv | Configuration management |

### Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| **CSS Framework** | Bootstrap 5.3 | Responsive UI components |
| **Icons** | Bootstrap Icons + Deloitte Icons | UI iconography |
| **Templating** | Jinja2 | Server-side rendering |
| **JavaScript** | Vanilla JS (MVP) | Minimal interactivity |
| **Future Enhancement** | HTMX / Alpine.js | Enhanced UX (Phase 2) |

### Database

| Environment | Database | Notes |
|-------------|----------|-------|
| Development | SQLite | File-based, no setup |
| Production | PostgreSQL | Recommended for enterprise |

### Internationalization

| Component | Implementation |
|-----------|----------------|
| **Translation System** | Custom `translations.py` dictionary |
| **Supported Languages** | German (de), English (en) |
| **Default Language** | German (de) |
| **Language Storage** | Flask session (`session['lang']`) |
| **Template Access** | `{{ t('key') }}` via context processor |

---

## Project Structure

```
deloitte-taxops-calendar/
├── app.py                  # Application factory & routes (~1735 lines)
├── config.py               # Configuration classes
├── models.py               # SQLAlchemy models (~650 lines)
├── translations.py         # i18n dictionary (DE/EN)
├── init_db.py              # Database initialization
├── Pipfile                 # Dependencies (Pipenv)
├── Pipfile.lock            # Locked dependencies
├── .env                    # Environment variables (not in git)
├── .flaskenv               # Flask CLI configuration
│
├── instance/               # Instance-specific files
│   └── app.db              # SQLite database (dev)
│
├── migrations/             # Alembic migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       ├── ff00c7cfda61_add_taxops_calendar_models.py
│       ├── ebe34cad8512_add_multi_stage_approval_workflow_fields.py
│       ├── 76fd77636f22_add_taskpreset_model_for_predefined_.py
│       └── f34a3101bc19_add_taskreviewer_many_to_many_table_for_.py
│
├── docs/                   # Memory Bank documentation
│   ├── technicalConcept.md
│   ├── techContext.md
│   ├── systemPatterns.md
│   ├── productContext.md
│   ├── progress.md
│   └── activeContext.md
│
├── data/                   # JSON data files for presets
│   ├── steuerarten_aufgaben.json
│   └── Antraege.json
│
├── static/                 # Static assets
│   ├── Color Guide/        # Deloitte color documentation
│   ├── Deloitte Special Case Web Icons/
│   │   ├── SVG files/
│   │   └── Web font/
│   ├── Deloitte-Master-Logo/
│   │   └── DIGITAL/
│   ├── favicon/
│   └── Mobile App Icons/
│
├── templates/              # Jinja2 templates
│   ├── base.html           # Master layout
│   ├── index.html          # Home page
│   ├── login.html          # Authentication
│   ├── dashboard.html      # Main dashboard
│   ├── calendar.html       # Month calendar
│   ├── calendar_year.html  # Year calendar
│   ├── calendar_week.html  # Week calendar
│   ├── tasks/
│   │   ├── list.html       # Task list with filters
│   │   ├── detail.html     # Task detail with tabs
│   │   └── form.html       # Create/edit form
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── user_form.html
│   │   ├── entities.html
│   │   ├── entity_form.html
│   │   ├── tax_types.html
│   │   ├── tax_type_form.html
│   │   ├── presets.html
│   │   └── preset_form.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
└── uploads/                # User uploads (evidence files)
    └── task_*/             # Per-task folders with unique filenames
```

### Planned Structure Additions

```
├── blueprints/             # Modular route handlers
│   ├── __init__.py
│   ├── auth.py             # Login/logout routes
│   ├── main.py             # Dashboard, calendar
│   ├── tasks.py            # Task CRUD, status changes
│   ├── admin.py            # Entity, user, template management
│   └── api.py              # REST endpoints (optional)
│
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── task_service.py     # Task lifecycle management
│   ├── import_service.py   # Excel import logic
│   ├── export_service.py   # Excel export logic
│   └── audit_service.py    # Audit logging
│
├── forms/                  # WTForms form classes
│   ├── __init__.py
│   ├── auth_forms.py
│   ├── task_forms.py
│   ├── entity_forms.py
│   └── import_forms.py
│
└── utils/                  # Helper utilities
    ├── __init__.py
    ├── decorators.py       # Custom decorators
    ├── helpers.py          # Utility functions
    └── validators.py       # Custom validators
```

---

## Dependencies

### Current (from Pipfile)

```toml
[packages]
flask = "*"
flask-sqlalchemy = "*"
flask-login = "*"
flask-wtf = "*"
werkzeug = "*"
python-dotenv = "*"

[dev-packages]

[requires]
python_version = "3.9"
```

### Required Additions for TaxOps Calendar

```toml
[packages]
# Existing
flask = "*"
flask-sqlalchemy = "*"
flask-login = "*"
flask-wtf = "*"
werkzeug = "*"
python-dotenv = "*"

# New - Database migrations
flask-migrate = "*"

# New - Excel processing
openpyxl = "*"

# New - Date handling
python-dateutil = "*"

# New - File uploads
flask-uploads = "*"          # Or handle manually

[dev-packages]
pytest = "*"
pytest-flask = "*"
faker = "*"                  # Test data generation
```

### Production Additions (Deployment)

```toml
[packages]
# Production database
psycopg2-binary = "*"        # PostgreSQL adapter

# Production server
gunicorn = "*"

# Background jobs (Phase 2)
apscheduler = "*"            # Simple scheduler
# OR
# celery = "*"               # Distributed tasks
# redis = "*"                # Message broker
```

---

## Development Setup

### Prerequisites

- Python 3.9+
- Pipenv (`pip install pipenv`)
- Git

### Initial Setup

```bash
# Clone repository
cd deloitte-taxops-calendar

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Create .env file
cat > .env << EOF
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/app.db
EOF

# Initialize database
flask initdb

# Create admin user
flask createadmin

# Run development server
flask run
```

### Database Migrations (Alembic)

```bash
# Initialize migrations (first time only)
flask db init

# Create migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback one version
flask db downgrade
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_tasks.py
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_APP` | Application entry point | `app.py` |
| `FLASK_ENV` | Environment mode | `development` |
| `SECRET_KEY` | Session encryption key | (required) |
| `DATABASE_URL` | Database connection string | SQLite |
| `UPLOAD_FOLDER` | Path for file uploads | `uploads/` |
| `MAX_CONTENT_LENGTH` | Max upload size (bytes) | 16MB |

---

## Deloitte Branding Integration

### CSS Variables Available

The base template includes the complete Deloitte 2024 color palette:

```css
/* Primary */
--dtt-green: #86BC25;
--dtt-black: #000000;

/* Status Colors */
--dtt-danger-red: #DA291C;      /* Overdue */
--dtt-warning-orange: #ED8B00;  /* Due Soon */
--dtt-sec-blue-4: #0076A8;      /* Submitted */
--dtt-sec-teal-6: #007680;      /* In Review */
--dtt-sec-green-5: #009A44;     /* Completed */

/* Bootstrap Mapped */
--bs-primary: var(--dtt-green);
--bs-danger: var(--dtt-danger-red);
--bs-success: var(--dtt-sec-green-5);
```

### Status Badge Classes (Implemented)

```css
/* Status colors using Deloitte palette */
.badge-status--draft { background-color: var(--dtt-cool-gray-6); }
.badge-status--due-soon { background-color: var(--dtt-warning-orange); }
.badge-status--overdue { background-color: var(--dtt-danger-red); }
.badge-status--submitted { background-color: var(--dtt-sec-blue-4); }
.badge-status--in-review { background-color: var(--dtt-sec-teal-6); }
.badge-status--approved { background-color: var(--dtt-sec-green-5); }
.badge-status--completed { background-color: var(--dtt-sec-green-5); }
.badge-status--rejected { background-color: var(--dtt-danger-red); }
```

---

## Database Models

### Core Models (models.py ~650 lines)

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `User` | User accounts | email, name, role, password_hash |
| `Entity` | Legal entities | name, country, group_id, is_active |
| `TaxType` | Tax categories | code, name, description |
| `TaskTemplate` | Reusable templates | keyword, tax_type_id, description |
| `Task` | Core tasks | title, entity_id, due_date, status, owner_id |
| `TaskReviewer` | Multi-reviewer tracking | task_id, user_id, has_approved, approved_at |
| `TaskEvidence` | File/link attachments | task_id, evidence_type, file_path, url |
| `Comment` | Discussion threads | task_id, text, created_by_id |
| `TaskPreset` | Predefined templates | title, category, tax_type, description |
| `AuditLog` | Activity logging | action, entity_type, entity_id, user_id |

### TaskReviewer Model (Multi-Reviewer Support)

```python
class TaskReviewer(db.Model):
    __tablename__ = 'task_reviewer'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order = db.Column(db.Integer, default=1)
    has_approved = db.Column(db.Boolean, default=False)
    approved_at = db.Column(db.DateTime)
    approval_note = db.Column(db.Text)
    has_rejected = db.Column(db.Boolean, default=False)
    rejected_at = db.Column(db.DateTime)
    rejection_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User')
    
    # Unique constraint: one reviewer per task
    __table_args__ = (db.UniqueConstraint('task_id', 'user_id', name='unique_task_reviewer'),)
```

---

## IDE Configuration

### VSCode Recommended Extensions

- Python (Microsoft)
- Pylance
- Flask Snippets
- Jinja2 Snippet Kit
- SQLite Viewer
- GitLens

### VSCode Settings (`.vscode/settings.json`)

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.associations": {
    "*.html": "jinja-html"
  }
}
```
